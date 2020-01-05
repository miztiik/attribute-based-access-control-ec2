from aws_cdk import (
        aws_iam as iam,
        aws_ec2 as ec2,
        aws_ssm as ssm,
        core
)

from custom_resource.iam_user_tagger_cdk import iam_user_tagger
from custom_resource.random_string_generator_cdk import random_string_generator

class AbacEc2DemoStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Lets generate a password for our user
        shiny_new_pass = random_string_generator(
            self,
            "shinyNewPasswordGenerator",
            Length=20
        )


        # Lets create a user
        projectRedUser1redRosy = iam.User(
            self,
            "projectRedUser1redRosy",
            user_name="redRosy",
            password=core.SecretValue.plain_text(shiny_new_pass.response)
        )

        teamUnicornGrp = iam.Group(
            self,
            "teamUnicornGrp",
            group_name="teamUnicorn"
        )

        # Add Users To Group
        teamUnicornGrp.add_user(projectRedUser1redRosy)

        # blueGrp1.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess"))
        ##############################################
        # We need a custom resource to TAG IAM Users #
        ##############################################

        iamUserTaggerResp = iam_user_tagger(
            self, "iamTagger",
            message=[
                {
                    "user":projectRedUser1redRosy.user_name, 
                    "tags":[
                        {'Key': 'teamName','Value':'teamUnicorn'},
                        {'Key': 'projectName','Value':'projectRed'}
                    ]
                }
            ]
        )

        # Lets Create the IAM Role
        # Uses belonging to this group, will be able to asume this role based on tag validation
        accountId=core.Aws.ACCOUNT_ID
        teamUnicornProjectRedRole = iam.Role(
            self,
            'unicornTeamProjectRedRoleId',
            assumed_by=iam.AccountPrincipal(f"{accountId}"),
            role_name="teamUnicornProjectRedRole"
        )
        core.Tag.add(teamUnicornProjectRedRole, key="teamName",value="teamUnicorn")
        core.Tag.add(teamUnicornProjectRedRole, key="projectName",value="projectRed")


        """
        # Allow Group to Assume Role
        # The role will have naming convention like,
        <TEAM-NAME><PROJECT-NAME>ROLE
        For Ex: unicornTeamProjectRedRole
        """
        grpStmt1=iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=[f"arn:aws:iam::{accountId}:role/teamUnicornProject*"],
                actions=["sts:AssumeRole"],
                conditions={ "StringEquals": { "iam:ResourceTag/teamName": "${aws:PrincipalTag/teamName}",
                                               "iam:ResourceTag/projectName": "${aws:PrincipalTag/projectName}" 
                                            }
                        }
            )
        grpStmt1.sid="AllowGroupMembersToAssumeRoleMatchingTeamName"
        # Attach the policy to the group
        teamUnicornGrp.add_to_policy( grpStmt1 )

        # Add Permissions to the Role
        roleStmt0=iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=[ "*" ],
                actions=[
                    "ec2:Describe*",
                    "cloudwatch:Describe*",
                    "cloudwatch:Get*",
                ]
            )
        roleStmt0.sid="AllowUserToDescribeInstances"
        teamUnicornProjectRedRole.add_to_policy( roleStmt0 )

        roleStmt1a=iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=[
                "arn:aws:ec2:*::image/*",
                "arn:aws:ec2:*::snapshot/*",
                "arn:aws:ec2:*:*:subnet/*",
                "arn:aws:ec2:*:*:network-interface/*",
                "arn:aws:ec2:*:*:security-group/*",
                "arn:aws:ec2:*:*:key-pair/*"
                ],
            actions=[
                "ec2:RunInstances"
            ]
        )
        roleStmt1a.sid="AllowRunInstances"
        teamUnicornProjectRedRole.add_to_policy( roleStmt1a )

        roleStmt1b=iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=[
                "arn:aws:ec2:*:*:instance/*",
                "arn:aws:ec2:*:*:volume/*",
                ],
            actions=[
                "ec2:CreateVolume",
                "ec2:RunInstances"
            ],
            conditions={ "StringEquals": 
                            { 
                                "aws:RequestTag/teamName": "${aws:PrincipalTag/teamName}",
                                "aws:RequestTag/projectName": "${aws:PrincipalTag/projectName}"
                            },
                        "ForAllValues:StringEquals": {
                            "aws:TagKeys": [
                                "teamName",
                                "projectName"
                            ]
                        }
                    }
            )

        roleStmt1b.sid="AllowRunInstancesWithRestrictionsRequiredTags"
        teamUnicornProjectRedRole.add_to_policy( roleStmt1b )

        roleStmt2=iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=[
                    "arn:aws:ec2:*:*:instance/*",
                    "arn:aws:ec2:*:*:volume/*"
                    ],
                actions=["ec2:CreateTags"],
                conditions={ 
                    "StringEquals":{ 
                        "aws:RequestTag/teamName": "${aws:PrincipalTag/teamName}",
                        "aws:RequestTag/projectName": "${aws:PrincipalTag/projectName}" 
                    },
                    "ForAllValues:StringEquals" :{
                        "aws:TagKeys":[ "projectName", "teamName"]
                    },
                    "StringEquals": { "ec2:CreateAction": "RunInstances" }
                }
            )
        roleStmt2.sid="AllowCreateTagsIfRequestingValidTags"
        teamUnicornProjectRedRole.add_to_policy( roleStmt2 )

        roleStmt3=iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=[
                    "arn:aws:ec2:*:*:instance/*",
                    "arn:aws:ec2:*:*:volume/*"
                    ],
                actions=[
                    "ec2:RebootInstances",
                    "ec2:TerminateInstances",
                    "ec2:StartInstances",
                    "ec2:StopInstances"
                ],
                conditions={ "StringEquals": 
                                { 
                                    "ec2:ResourceTag/teamName": "${aws:PrincipalTag/teamName}",
                                    "ec2:ResourceTag/projectName": "${aws:PrincipalTag/projectName}"
                                }
                        }
            )
        roleStmt3.sid="AllowInstanceManagementIfTagsMatch"
        teamUnicornProjectRedRole.add_to_policy( roleStmt3 )

        # Lets create couple of instances to test
        vpc = ec2.Vpc(
                self, "abacVPC",
                cidr="10.13.0.0/21",
                max_azs=2,
                nat_gateways=0,
                subnet_configuration=[
                    ec2.SubnetConfiguration(name="pubSubnet", cidr_mask=24, subnet_type=ec2.SubnetType.PUBLIC)
                ]
            )
        
        # Tag all VPC Resources
        core.Tag.add(vpc,key="Owner",value="KonStone",include_resource_types=[])
        core.Tag.add(vpc,key="teamName",value="teamUnicorn",include_resource_types=[])

        # We are using the latest AMAZON LINUX AMI
        ami_id = ec2.AmazonLinuxImage(generation = ec2.AmazonLinuxGeneration.AMAZON_LINUX_2).get_image(self).image_id
        
        red_web_inst = ec2.CfnInstance(self,
            "redWebInstance01",
            image_id = ami_id,
            instance_type = "t2.micro",
            monitoring = False,
            tags = [
                { "key": "teamName", "value": "teamUnicorn" },
                { "key": "projectName", "value": "projectRed" },
                { "key": "Name", "value": "projectRed-Web" }
            ],
            network_interfaces = [{
                "deviceIndex": "0",
                "associatePublicIpAddress": True,
                "subnetId": vpc.public_subnets[0].subnet_id,
                # "groupSet": [web_sg.security_group_id]
            }], #https: //github.com/aws/aws-cdk/issues/3419
        )
        # core.Tag.add(red_web_inst,key="Owner",value="KonStone",include_resource_types=[])

        blue_web_inst = ec2.CfnInstance(self,
            "blueWebInstance01",
            image_id = ami_id,
            instance_type = "t2.micro",
            monitoring = False,
            tags = [
                { "key": "teamName", "value": "teamUnicorn" },
                { "key": "projectName", "value": "projectBlue" },
                { "key": "Name", "value": "projectBlue-Web" }
            ],
            network_interfaces = [{
                "deviceIndex": "0",
                "associatePublicIpAddress": True,
                "subnetId": vpc.public_subnets[0].subnet_id,
                # "groupSet": [web_sg.security_group_id]
            }], #https: //github.com/aws/aws-cdk/issues/3419
        )
        # core.Tag.add(blue_web_inst,key="Owner",value="KonStone",include_resource_types=[])

        # https://signin.aws.amazon.com/switchrole?roleName=teamUnicornProjectRedRole&account=lint3r
        role_login_url = (f"https://signin.aws.amazon.com/switchrole?&account={accountId}"
                            f"&roleName={teamUnicornProjectRedRole.role_name}"
        )
        output1 = core.CfnOutput(self,
                    "Red-Rosy-AssumeRoleUrl",
                    value=role_login_url,
                    description="Url to login & assume role"
        )
        output2 = core.CfnOutput(self,
            "redRosy_user_password",
            value=shiny_new_pass.response,
            description="redRosy user password"
        )
        # Publish the custom resource output
        output3 = core.CfnOutput(
            self, "IAMUserTaggerResponseMessage",
            description="IAM User Tagging Successful",
            value=iamUserTaggerResp.response,
        )
        # Publish WebInstances ID and Tags
        output4 = core.CfnOutput(
            self, "ProjectRed-Web-Instance",
            description="Project Red Web Instance Publice IP",
            value=core.Fn.get_att(logical_name_of_resource="redWebInstance01",attribute_name="PublicIp").to_string(),
        )
        output5 = core.CfnOutput(
            self, "ProjectBlue-Web-Instance",
            description="Project Blue Web Instance Publice IP",
            value=core.Fn.get_att(logical_name_of_resource="blueWebInstance01",attribute_name="PublicIp").to_string(),
        )
        output10 = core.CfnOutput(self,
            "Red-Rosy-User-Login-Url",
            value=(
                    f"https://{core.Aws.ACCOUNT_ID}.signin.aws.amazon.com/console"
                ),
            description=f"The URL for Rosy to Login"
        )