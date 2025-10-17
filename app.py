#!/usr/bin/env python3
import os

import aws_cdk as cdk

from maxmind_geolite2.maxmind_geolite2_history import MaxmindGeolite2History
from maxmind_geolite2.maxmind_geolite2_stack import MaxmindGeolite2Stack

app = cdk.App()

MaxmindGeolite2History(
    app, 'MaxmindGeolite2History',
    env = cdk.Environment(
        account = os.getenv('CDK_DEFAULT_ACCOUNT'),
        region = 'us-east-1'
    ),
    synthesizer = cdk.DefaultStackSynthesizer(
        qualifier = '4n6ir'
    )
)

MaxmindGeolite2Stack(
    app, 'MaxmindGeolite2Stack',
    env = cdk.Environment(
        account = os.getenv('CDK_DEFAULT_ACCOUNT'),
        region = 'us-east-1'
    ),
    synthesizer = cdk.DefaultStackSynthesizer(
        qualifier = '4n6ir'
    )
)

cdk.Tags.of(app).add('Alias','4n6ir.com')
cdk.Tags.of(app).add('GitHub','https://github.com/jblukach/maxmind-geolite2')

app.synth()