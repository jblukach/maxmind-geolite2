import cdk_nag

from aws_cdk import (
    Aspects,
    Duration,
    RemovalPolicy,
    Stack,
    aws_events as _events,
    aws_events_targets as _targets,
    aws_iam as _iam,
    aws_lambda as _lambda,
    aws_logs as _logs,
    aws_logs_destinations as _destinations,
    aws_s3 as _s3,
    aws_s3_deployment as _deployment,
    aws_sns_subscriptions as _subs,
    aws_ssm as _ssm
)

from constructs import Construct

class MaxmindGeolite2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        Aspects.of(self).add(
            cdk_nag.AwsSolutionsChecks(
                log_ignores = True,
                verbose = True
            )
        )

        cdk_nag.NagSuppressions.add_stack_suppressions(
            self, suppressions = [
                {'id': 'AwsSolutions-IAM4','reason': 'GitHub Issue'},
                {'id': 'AwsSolutions-IAM5','reason': 'GitHub Issue'},
                {'id': 'AwsSolutions-S1','reason': 'GitHub Issue'}
            ]
        )

        account = Stack.of(self).account
        region = Stack.of(self).region

    ### LAMBDA LAYER ###

        layer = _lambda.LayerVersion.from_layer_version_arn(
            self, 'layer',
            layer_version_arn = 'arn:aws:lambda:'+region+':070176467818:layer:getpublicip:3'
        )

    ### STORAGE ###

        maxmind_api_key_secure_ssm_parameter = '/maxmind/geolite2/api'

        bucket = _s3.Bucket(
            self, 'bucket',
            encryption = _s3.BucketEncryption.S3_MANAGED,
            block_public_access = _s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy = RemovalPolicy.DESTROY,
            enforce_ssl = True,
            versioned = True
        )

        bucket.add_lifecycle_rule(
            expiration = Duration.days(21),
            noncurrent_version_expiration = Duration.days(1),
            prefix = 'geoip2.zip'
        )

        bucket.add_lifecycle_rule(
            expiration = Duration.days(21),
            noncurrent_version_expiration = Duration.days(1),
            prefix = 'GeoLite2-City.mmdb'
        )

        bucket.add_lifecycle_rule(
            expiration = Duration.days(21),
            noncurrent_version_expiration = Duration.days(1),
            prefix = 'GeoLite2-ASN.mmdb'
        )

        deployment = _deployment.BucketDeployment(
            self, 'DeployFunctionFile',
            sources = [_deployment.Source.asset('code')],
            destination_bucket = bucket,
            prune = False
        )

    ### ERROR ###

        error = _lambda.Function.from_function_arn(
            self, 'error',
            'arn:aws:lambda:'+region+':'+account+':function:shipit-error'
        )

        timeout = _lambda.Function.from_function_arn(
            self, 'timeout',
            'arn:aws:lambda:'+region+':'+account+':function:shipit-timeout'
        )

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
            function_name = 'geo',
            runtime = _lambda.Runtime.PYTHON_3_9,
            code = _lambda.Code.from_asset('search'),
            handler = 'search.handler',
            timeout = Duration.seconds(60),
            role = role,
            memory_size = 512,
            layers = [
                layer
            ]
        )

        url = search.add_function_url(
            auth_type = _lambda.FunctionUrlAuthType.NONE
        )

        parameter = _ssm.StringParameter(
            self, 'parameter',
            description = 'MaxMind GEOLite2 Lambda URL',
            parameter_name = '/maxmind/geolite2/url',
            string_value = url.url,
            tier = _ssm.ParameterTier.STANDARD,
        )

        searchlogs = _logs.LogGroup(
            self, 'searchlogs',
            log_group_name = '/aws/lambda/'+search.function_name,
            retention = _logs.RetentionDays.ONE_DAY,
            removal_policy = RemovalPolicy.DESTROY
        )

        searchsub = _logs.SubscriptionFilter(
            self, 'searchsub',
            log_group = searchlogs,
            destination = _destinations.LambdaDestination(error),
            filter_pattern = _logs.FilterPattern.all_terms('ERROR')
        )

        searchtime= _logs.SubscriptionFilter(
            self, 'searchtime',
            log_group = searchlogs,
            destination = _destinations.LambdaDestination(timeout),
            filter_pattern = _logs.FilterPattern.all_terms('Task','timed','out')
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

        download = _lambda.DockerImageFunction(
            self, 'download',
            code = _lambda.DockerImageCode.from_image_asset('download'),
            timeout = Duration.seconds(900),
            role = build,
            environment = dict(
                S3_BUCKET = bucket.bucket_name,
                SSM_PARAMETER = maxmind_api_key_secure_ssm_parameter,
                LAMBDA_FUNCTION = search.function_name
            ),
            memory_size = 512
        )

        downloadlogs = _logs.LogGroup(
            self, 'downloadlogs',
            log_group_name = '/aws/lambda/'+download.function_name,
            retention = _logs.RetentionDays.ONE_DAY,
            removal_policy = RemovalPolicy.DESTROY
        )

        downloadsub = _logs.SubscriptionFilter(
            self, 'downloadsub',
            log_group = downloadlogs,
            destination = _destinations.LambdaDestination(error),
            filter_pattern = _logs.FilterPattern.all_terms('ERROR')
        )

        downloadtime= _logs.SubscriptionFilter(
            self, 'downloadtime',
            log_group = downloadlogs,
            destination = _destinations.LambdaDestination(timeout),
            filter_pattern = _logs.FilterPattern.all_terms('Task','timed','out')
        )

        event = _events.Rule(
            self, 'event',
            schedule=_events.Schedule.cron(
                minute='0',
                hour='11',
                month='*',
                week_day='WED',
                year='*'
            )
        )

        event.add_target(_targets.LambdaFunction(download))
