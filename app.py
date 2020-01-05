#!/usr/bin/env python3

from aws_cdk import core

from attribute_based_access_control_ec2.abac_ec2_stack import AbacEc2DemoStack

app = core.App()

# AbacEc2DemoStack( app, "ABAC-EC2")
# AbacEc2DemoStack( app, "ABAC-EC2", env=core.Environment(region="eu-west-1"))
AbacEc2DemoStack( app, "ABAC-EC2", env=core.Environment(region="us-east-1"))

# Tag the stack resources
core.Tag.add(app,key="Owner",value=app.node.try_get_context('owner'))
core.Tag.add(app,key="OwnerProfile",value=app.node.try_get_context('github_profile'))
core.Tag.add(app,key="ToKnowMore",value=app.node.try_get_context('youtube_profile'))

app.synth()

"""
env_EU = core.Environment(account="8373873873", region="eu-west-1")
env_USA = core.Environment(account="2383838383", region="us-west-2")

MyFirstStack(app, "first-stack-us", env=env_USA, encryption=False)
MyFirstStack(app, "first-stack-eu", env=env_EU, encryption=True)
"""