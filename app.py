#!/usr/bin/env python3
import os

import aws_cdk as cdk

from maxmind_geolite2.maxmind_geolite2_stack import MaxmindGeolite2Stack

app = cdk.App()

MaxmindGeolite2Stack(
    app, 'MaxmindGeolite2Stack',
    env = cdk.Environment(
        account = os.getenv('CDK_DEFAULT_ACCOUNT'),
        region = 'us-west-2'
    ),
    synthesizer = cdk.DefaultStackSynthesizer(
        qualifier = '4n6ir'
    )
)

cdk.Tags.of(app).add('Alias','Tacklebox')
cdk.Tags.of(app).add('GitHub','https://github.com/4n6ir/maxmind-geolite2')

app.synth()
