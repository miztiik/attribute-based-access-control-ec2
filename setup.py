import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="attribute_based_access_control_ec2",
    version="0.0.1",

    description="attribute_based_access_control_ec2",
    long_description=attribute_based_access_control_ec2,
    long_description_content_type="text/markdown",

    author="miztiik",

    package_dir={"": "attribute_based_access_control_ec2"},
    packages=setuptools.find_packages(where="attribute_based_access_control_ec2"),

    install_requires=[
        "aws-cdk.core",
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
