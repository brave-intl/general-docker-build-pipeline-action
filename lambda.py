import boto3
import os

def easy_generalized_deploy(owner, repo, branch, sourceVersion):
    AWS_ACCOUNT_ID = os.environ["AWS_ACCOUNT_ID"]
    CODE_BUILD_PROJECT = os.environ["CODE_BUILD_PROJECT"]
    REGION = os.environ["REGION"]

    # Create ECR repo if it does not exist
    client = boto3.client("ecr", region_name=REGION)
    response = client.describe_repositories(
        registryId=AWS_ACCOUNT_ID,
    )
    ecr_repos = response["repositories"]
    should_create_ecr_repo = True
    for ecr_repo in ecr_repos:
        if ecr_repo["repositoryName"] == repo:
            should_create_ecr_repo = False

    if should_create_ecr_repo:
        response = client.create_repository(
            repositoryName=repo,
            tags=[],
            imageTagMutability="IMMUTABLE",
            imageScanningConfiguration={
                "scanOnPush": True
            }
        )

    # Derive git url
    git_repo_url = "https://github.com/{}/{}.git".format(owner, repo)

    # Derive image tag
    image_tag = "{}:{}-{}".format(repo, branch, sourceVersion)

    # Start run build
    client = boto3.client("codebuild", region_name=REGION)
    response = client.start_build(
        buildspec="TODO",
        projectName=CODE_BUILD_PROJECT,
        sourceVersion=sourceVersion,
        sourceLocationOverride=git_repo_url,
        sourceTypeOverride="GITHUB",
        environmentVariablesOverride=[{"name": "IMAGE_TAG", "value": image_tag}]
    )

    return response
