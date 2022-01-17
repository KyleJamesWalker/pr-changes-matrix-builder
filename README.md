# PR Changes Matrix Builder
This Action will generate a output variable that can be used to generate a
dynamic matrix job.

This is often need for repos that contain many apps, here are a few examples:

 * Terraform Infrastructure: At my current job we have a single repo with all
   of our cloud infrastructure. Each folder is deployed individually, so being
   able to detect what folders have been changed can build a matrix for each
   terraform plan command.

 * ArgoCD: This is a single repo with all of our ArgoCD apps. Each folder is
   deployed individually, so being able to detect what folders have been changed
   can build a matrix for each ArgoCD command.

 * Helm chart: At my current job we have a collection of generic helm charts.
   Each folder is a chart that is individually deployed, tagged, and released.

This action is based on a quick POC in
[KyleJamesWalker/action-playground PR#3](https://github.com/KyleJamesWalker/action-playground/pull/3)
and expands on a command like:

``` bash
# Github Command
$ gh pr view 3 --repo KyleJamesWalker/action-playground --json files --jq '.files.[].path' | cut -d "/" -f1 | grep -v '[\\|\.]' | sort | uniq | jq  --raw-input .

# Example Output
"example_1"
"example_2"
```

# Docker Image Sizes
 * kylejameswalker/pr-changes-matrix-builder-pytest 308MB
 * kylejameswalker/pr-changes-matrix-builder        254MB
