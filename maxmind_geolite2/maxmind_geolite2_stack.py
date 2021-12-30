from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_events as _events,
    aws_events_targets as _targets,
    aws_iam as _iam,
    aws_lambda as _lambda,
    aws_logs as _logs,
    aws_s3 as _s3,
    aws_s3_deployment as _deployment,
    aws_ssm as _ssm
)

from constructs import Construct

class MaxmindGeolite2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        maxmind_api_key_secure_ssm_parameter = '/maxmind/geolite2/api'

        bucket = _s3.Bucket(
            self, 'bucket', versioned = True,
            encryption = _s3.BucketEncryption.S3_MANAGED,
            block_public_access = _s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy = RemovalPolicy.DESTROY
        )

        deployment = _deployment.BucketDeployment(
            self, 'DeployFunctionFile',
            sources = [_deployment.Source.asset('code')],
            destination_bucket = bucket,
            prune = False
        )

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
            runtime = _lambda.Runtime.PYTHON_3_9,
            code = _lambda.Code.from_asset('search'),
            handler = 'search.handler',
            timeout = Duration.seconds(30),
            role = role,
            memory_size = 512
        )

        searchlogs = _logs.LogGroup(
            self, 'searchlogs',
            log_group_name = '/aws/lambda/'+search.function_name,
            retention = _logs.RetentionDays.ONE_DAY,
            removal_policy = RemovalPolicy.DESTROY
        )

        searchmonitor = _ssm.StringParameter(
            self, 'searchmonitor',
            description = 'MaxMind GeoLite2 Search Monitor',
            parameter_name = '/maxmind/geolite2/monitor/search',
            string_value = '/aws/lambda/'+search.function_name,
            tier = _ssm.ParameterTier.STANDARD,
        )

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

        downloadmonitor = _ssm.StringParameter(
            self, 'downloadmonitor',
            description = 'MaxMind GeoLite2 Download Monitor',
            parameter_name = '/maxmind/geolite2/monitor/download',
            string_value = '/aws/lambda/'+download.function_name,
            tier = _ssm.ParameterTier.STANDARD,
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
