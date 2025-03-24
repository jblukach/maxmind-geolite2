from aws_cdk import (
    Duration,
    RemovalPolicy,
    Size,
    Stack,
    aws_apigatewayv2 as _api,
    aws_apigatewayv2_integrations as _integrations,
    aws_certificatemanager as _acm,
    aws_events as _events,
    aws_events_targets as _targets,
    aws_iam as _iam,
    aws_lambda as _lambda,
    aws_logs as _logs,
    aws_route53 as _route53,
    aws_route53_targets as _r53targets,
    aws_s3 as _s3,
    aws_s3_deployment as _deployment,
    aws_ssm as _ssm
)

from constructs import Construct

class MaxmindGeolite2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

    ### LAMBDA LAYERS ###

        pkggeoip2 = _ssm.StringParameter.from_string_parameter_arn(
            self, 'pkggeoip2',
            'arn:aws:ssm:us-east-1:070176467818:parameter/pkg/geoip2'
        )

        geoip2 = _lambda.LayerVersion.from_layer_version_arn(
            self, 'geoip2',
            layer_version_arn = pkggeoip2.string_value
        )

        pkgmaxminddb = _ssm.StringParameter.from_string_parameter_arn(
            self, 'pkgmaxminddb',
            'arn:aws:ssm:us-east-1:070176467818:parameter/pkg/maxminddb'
        )

        maxminddb = _lambda.LayerVersion.from_layer_version_arn(
            self, 'maxminddb',
            layer_version_arn = pkgmaxminddb.string_value
        )

        organization = _ssm.StringParameter.from_string_parameter_arn(
            self, 'organization',
            'arn:aws:ssm:us-east-1:070176467818:parameter/root/organization'
        )

        pkgrequests = _ssm.StringParameter.from_string_parameter_arn(
            self, 'pkgrequests',
            'arn:aws:ssm:us-east-1:070176467818:parameter/pkg/requests'
        )

        requests = _lambda.LayerVersion.from_layer_version_arn(
            self, 'requests',
            layer_version_arn = pkgrequests.string_value
        )

    ### S3 BUCKET ###

        bucket = _s3.Bucket(
            self, 'bucket',
            bucket_name = 'maxmindgeolite2downloads',
            encryption = _s3.BucketEncryption.S3_MANAGED,
            block_public_access = _s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy = RemovalPolicy.DESTROY,
            auto_delete_objects = True,
            enforce_ssl = True,
            versioned = False
        )

        deployment = _deployment.BucketDeployment(
            self, 'DeployFunctionFile',
            sources = [_deployment.Source.asset('code')],
            destination_bucket = bucket,
            prune = False
        )

        bucket_policy = _iam.PolicyStatement(
            effect = _iam.Effect(
                'ALLOW'
            ),
            principals = [
                _iam.AnyPrincipal()
            ],
            actions = [
                's3:ListBucket'
            ],
            resources = [
                bucket.bucket_arn
            ],
            conditions = {"StringEquals": {"aws:PrincipalOrgID": organization.string_value}}
        )

        bucket.add_to_resource_policy(bucket_policy)

        object_policy = _iam.PolicyStatement(
            effect = _iam.Effect(
                'ALLOW'
            ),
            principals = [
                _iam.AnyPrincipal()
            ],
            actions = [
                's3:GetObject'
            ],
            resources = [
                bucket.arn_for_objects('*')
            ],
            conditions = {"StringEquals": {"aws:PrincipalOrgID": organization.string_value}}
        )

        bucket.add_to_resource_policy(object_policy)

    ### SEARCH ###

        role = _iam.Role(
            self, 'role',
            assumed_by = _iam.ServicePrincipal(
                'lambda.amazonaws.com'
            )
        )

        role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name(
                'service-role/AWSLambdaBasicExecutionRole'
            )
        )

        search = _lambda.Function(
            self, 'search',
            runtime = _lambda.Runtime.PYTHON_3_13,
            architecture = _lambda.Architecture.ARM_64,
            code = _lambda.Code.from_asset('search'),
            handler = 'search.handler',
            timeout = Duration.seconds(7),
            memory_size = 128,
            role = role,
            layers = [
                geoip2,
                maxminddb
            ]
        )

        searchlogs = _logs.LogGroup(
            self, 'searchlogs',
            log_group_name = '/aws/lambda/'+search.function_name,
            retention = _logs.RetentionDays.THIRTEEN_MONTHS,
            removal_policy = RemovalPolicy.DESTROY
        )

    ### BUILD ###

        build = _iam.Role(
            self, 'build',
            assumed_by = _iam.ServicePrincipal(
                'lambda.amazonaws.com'
            )
        )

        build.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name(
                'service-role/AWSLambdaBasicExecutionRole'
            )
        )

        build.add_to_policy(
            _iam.PolicyStatement(
                actions = [
                    'lambda:UpdateFunctionCode',
                    's3:GetObject',
                    's3:PutObject',
                    'ssm:GetParameter'
                ],
                resources = [
                    '*'
                ]
            )
        )

        download = _lambda.Function(
            self, 'download',
            runtime = _lambda.Runtime.PYTHON_3_13,
            architecture = _lambda.Architecture.ARM_64,
            code = _lambda.Code.from_asset('download'),
            handler = 'download.handler',
            environment = dict(
                S3_BUCKET = bucket.bucket_name,
                SSM_PARAMETER_ACCT = '/maxmind/geolite2/account',
                SSM_PARAMETER_KEY = '/maxmind/geolite2/api',
                SSM_PARAMETER_GIT = '/github/releases',
                LAMBDA_FUNCTION = search.function_name
            ),
            ephemeral_storage_size = Size.gibibytes(1),
            timeout = Duration.seconds(900),
            memory_size = 1024,
            role = build,
            layers = [
                requests
            ]
        )

        downloadlogs = _logs.LogGroup(
            self, 'downloadlogs',
            log_group_name = '/aws/lambda/'+download.function_name,
            retention = _logs.RetentionDays.ONE_WEEK,
            removal_policy = RemovalPolicy.DESTROY
        )

        event = _events.Rule(
            self, 'event',
            schedule=_events.Schedule.cron(
                minute='0',
                hour='0',
                month='*',
                week_day='WED',
                year='*'
            )
        )

        event.add_target(
            _targets.LambdaFunction(
                download
            )
        )

        eventtwo = _events.Rule(
            self, 'eventtwo',
            schedule=_events.Schedule.cron(
                minute='0',
                hour='0',
                month='*',
                week_day='SAT',
                year='*'
            )
        )

        eventtwo.add_target(
            _targets.LambdaFunction(
                download
            )
        )

    ### HOSTZONE ###

        hostzoneid = _ssm.StringParameter.from_string_parameter_attributes(
            self, 'hostzoneid',
            parameter_name = '/network/hostzone'
        )

        hostzone = _route53.HostedZone.from_hosted_zone_attributes(
             self, 'hostzone',
             hosted_zone_id = hostzoneid.string_value,
             zone_name = '4n6ir.com'
        )   

    ### ACM CERTIFICATE ###

        acm = _acm.Certificate(
            self, 'acm',
            domain_name = 'geo.4n6ir.com',
            validation = _acm.CertificateValidation.from_dns(hostzone)
        )

        domain = _api.DomainName(
            self, 'domain',
            domain_name = 'geo.4n6ir.com',
            certificate = acm
        )

    ### API LOG ROLE ###

        apirole = _iam.Role(
            self, 'apirole', 
            assumed_by = _iam.ServicePrincipal(
                'apigateway.amazonaws.com'
            )
        )

        apirole.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name(
                'service-role/AmazonAPIGatewayPushToCloudWatchLogs'
            )
        )

    ### API GATEWAY ###

        integration = _integrations.HttpLambdaIntegration(
            'integration', search
        )

        api = _api.HttpApi(
            self, 'api',
            api_name = 'maxmind-geolite2',
            description = 'This product includes GeoLite2 data created by MaxMind, available from https://www.maxmind.com.',
            default_domain_mapping = _api.DomainMappingOptions(
                domain_name = domain
            )
        )

        api.add_routes(
            path = '/',
            methods = [
                _api.HttpMethod.GET
            ],
            integration = integration
        )
