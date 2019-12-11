#!/usr/bin/env python3

from aws_cdk import core

from attribute_based_access_control_ec2.attribute_based_access_control_ec2_stack import AttributeBasedAccessControlEc2Stack


app = core.App()
AttributeBasedAccessControlEc2Stack(app, "attribute-based-access-control-ec2")

app.synth()
