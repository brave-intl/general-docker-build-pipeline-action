## General docker build pipeline action

A Github action that works in coordination with a [general docker build pipeline](https://github.com/brave-intl/general-docker-build-pipeline) to kick off a Lambda function that starts a build.

Run `npm run package` to create a new build.

## Why fork the AWS action?
The AWS CodeBuild run build action is great. It allows you to start a CodeBuild project via `git push` while also conveniently displaying the CodeBuild logs in the Github UI.  However, for our purposes this action falls short.

Since we're creating a generalized pipeline that can build images for all the apps in our org, the CodeBuild project poses a large security risk.  If the CodeBuild project were compromised, then an attacker could deploy arbitrary code on all of our applications.

In practice an attacker could do this by gaining control of one of our Github repos, then supplying a malicious buildspec file to the CodeBuild project at build time.  This would give them the ability to overwrite all the ECR repos in our organization.

Ideally we constrain the ECR repos that a malicious attacker can control to only the Github repo they have compromised.  We can achieve this by forking the AWS action and modifying it such that instead of invoking a CodeBuild project, the action invokes a Lambda function which then starts a CodeBuild project.  The difference is that the Lambda accepts a restricted set of parameters like repo name, repo owner, branch, and commit hash.  From these values the Lambda function computes the image tag and git url, and passes those to the CodeBuild.  By wrapping the call to CodeBuild with a Lambda, we ensure the CodeBuild project always pushes to the ECR repo associated with the source code it downloaded, and that an attacker can only push to the repo they compromised.
