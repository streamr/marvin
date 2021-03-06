#!/usr/bin/env bash

# Creds to https://github.com/X1011/git-directory-deploy

set -o errexit #abort if any command fails

# Create checksums of the static file archive
sha1sum ghdist/static.tar.gz | cut -f 1 -d " " > ghdist/static.tar.gz.sha1

# Make sure there's a .nojekyll file in the dist dir, so that Jekyll won't try to process the result
touch ghdist/.nojekyll

deploy_directory=ghdist
deploy_branch=gh-pages

#if no user identity is already set in the current git environment, use this:
default_username=deploy.sh
default_email=

#repository to deploy to. must be readable and writable.
repo=https://$GITHUB_TOKEN@github.com/streamr/marvin.git

if [[ $1 = "-v" || $1 = "--verbose" ]]; then
        verbose=true
fi

#echo expanded commands as they are executed (for debugging)
function enable_expanded_output {
        if [ $verbose ]; then
                set -o xtrace
                set +o verbose
        fi
}

#this is used to avoid outputting the repo URL, which may contain a secret token
function disable_expanded_output {
        if [ $verbose ]; then
                set +o xtrace
                set -o verbose
        fi
}

enable_expanded_output

commit_title=`git log -n 1 --format="%s" HEAD`
commit_hash=`git log -n 1 --format="%H" HEAD`

function set_user_id {
        if [[ -z `git config user.name` ]]; then
                git config user.name "$default_username"
        fi
        if [[ -z `git config user.email` ]]; then
                git config user.email "$default_email"
        fi
}

previous_branch=`git rev-parse --abbrev-ref HEAD`

if ! git diff --exit-code --quiet --cached; then
        echo Aborting due to uncommitted changes in the index
        exit 1
fi

disable_expanded_output
git fetch --force $repo $deploy_branch:$deploy_branch
enable_expanded_output

#make deploy_branch the current branch
git symbolic-ref HEAD refs/heads/$deploy_branch

#put the previously committed contents of deploy_branch branch into the index
git --work-tree "$deploy_directory" reset --mixed --quiet

git --work-tree "$deploy_directory" add --all

set +o errexit
diff=$(git --work-tree "$deploy_directory" diff --exit-code --quiet HEAD)$?
set -o errexit
case $diff in
        0) echo No changes to files in $deploy_directory. Skipping commit.;;
        1)
                set_user_id
                git --work-tree "$deploy_directory" commit -m \
                        "[Travis CI]: Deploy $commit_title"$'\n\n'"generated from commit $commit_hash"

                disable_expanded_output
                #--quiet is important here to avoid outputting the repo URL, which may contain a secret token
                git push --quiet $repo $deploy_branch
                enable_expanded_output
                ;;
        *)
                echo git diff exited with code $diff. Aborting.
                exit $diff
                ;;
esac

if [[ $previous_branch = "HEAD" ]]; then
        #we weren't on any branch before, so just set HEAD back to the commit it was on
        git update-ref --no-deref HEAD $commit_hash $deploy_branch
else
        git symbolic-ref HEAD refs/heads/$previous_branch
fi

git reset --mixed
