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

class MaxmindGeolite2History(Stack):

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

    ### IAM ROLE ###

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

        role.add_to_policy(
            _iam.PolicyStatement(
                actions = [
                    's3:GetObject',
                    's3:ListBucket'
                ],
                resources = [
                    '*'
                ]
            )
        )

        role.add_to_policy(
            _iam.PolicyStatement(
                actions = [
                    'apigateway:GET'
                ],
                resources = [
                    '*'
                ]
            )
        )

    ### HISTORY LAMBDA ###

        history = _lambda.Function(
            self, 'history',
            runtime = _lambda.Runtime.PYTHON_3_13,
            architecture = _lambda.Architecture.ARM_64,
            code = _lambda.Code.from_asset('history'),
            handler = 'history.handler',
            timeout = Duration.seconds(30),
            memory_size = 1024,
            role = role,
            layers = [
                geoip2,
                maxminddb
            ]
        )

        logs = _logs.LogGroup(
            self, 'historylogs',
            log_group_name = '/aws/lambda/'+history.function_name,
            retention = _logs.RetentionDays.THIRTEEN_MONTHS,
            removal_policy = RemovalPolicy.DESTROY
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
            domain_name = 'history.4n6ir.com',
            validation = _acm.CertificateValidation.from_dns(hostzone)
        )

        domain = _api.DomainName(
            self, 'domain',
            domain_name = 'history.4n6ir.com',
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
            'integration', history
        )

        api = _api.HttpApi(
            self, 'api',
            api_name = 'maxmind-geolite2-history',
            description = 'This product includes GeoLite2 data created by MaxMind, available from https://www.maxmind.com.',
            default_domain_mapping = _api.DomainMappingOptions(
                domain_name = domain
            ),
            ip_address_type = _api.IpAddressType.DUAL_STACK
        )

        api.add_routes(
            path = '/',
            methods = [
                _api.HttpMethod.GET
            ],
            integration = integration
        )

    ### DNS RECORDS

        ipv4dns = _route53.ARecord(
            self, 'ipv4dns',
            zone = hostzone,
            record_name = 'history.4n6ir.com',
            target = _route53.RecordTarget.from_alias(
                _r53targets.ApiGatewayv2DomainProperties(
                    domain.regional_domain_name,
                    domain.regional_hosted_zone_id
                )
            )
        )

        ipv6dns = _route53.AaaaRecord(
            self, 'ipv6dns',
            zone = hostzone,
            record_name = 'history.4n6ir.com',
            target = _route53.RecordTarget.from_alias(
                _r53targets.ApiGatewayv2DomainProperties(
                    domain.regional_domain_name,
                    domain.regional_hosted_zone_id
                )
            )
        )
