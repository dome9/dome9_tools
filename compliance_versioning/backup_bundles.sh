#!/bin/bash
# Alex Corstorphine alex@dome9.com
# 3/23/18
# Back up Dome9 compliance bundles to github

### store config file w/ key/secret/gitrepo
source ./secrets.cfg

### Files will be stored in /tmp/ Make the directories if they're not already there
# Bundles in Dome9 
if [ ! -d "/tmp/current_bundles" ]; then
	mkdir /tmp/current_bundles
fi

# # Pull down the current state from Git
cd /tmp/"$git_repo"

echo "Pulling latest state from git"
git pull

# Get the current bundles from Dome9
echo "Pulling current bundles from the Dome9 API"
echo ""

all_bundle_path="/tmp/current_bundles/all_bundles.json"
## Pull the current bundles down
curl -u $key:$secret -X GET 'https://api.dome9.com/v2/CompliancePolicy/' > $all_bundle_path

# Look through the Dome9 bundles and put all unique bundles into their own files
echo ""
echo "Saving the custom bundles into their own files"

# Copy all custom bundles into their own files. Skip the Dome9 managed content
i=1
while [ $i -lt `jq length $all_bundle_path` ]
	do
		bundle_id=`jq ".[$i].id" $all_bundle_path`
		if [ "$bundle_id" -gt 0 ] && [ "$bundle_id" -ne 21 ]; then
				#Send each bundle into its own file
				jq ".[$i]" $all_bundle_path > /tmp/current_bundles/"$bundle_id".json
		fi
		((i++))
	done

echo ""
echo "Comparing current bundles to what is currently in git"
echo ""
# Look through the files from git and compare them to what we just pulled from D9
for file in `ls /tmp/current_bundles/ | grep -v all_bundles.json`
	do
		bundle_name=`cat /tmp/current_bundles/"$file" | jq '.name'`
        echo "Checking bundle" $bundle_name

		if [ -f /tmp/"$git_repo"/"$file" ]; then

    		# echo "Bundle already in git - comparing last udpated dates"
    		git_date=`cat /tmp/$git_repo/"$file" | jq '.updatedTime'`
    		current_date=`cat /tmp/current_bundles/"$file" | jq '.updatedTime'`

    		if [ "$git_date" != "$current_date" ]; then 

    			echo "Bundle has been updated since last backup. Copying current version to git directory"
    			cp -f /tmp/current_bundles/"$file" /tmp/"$git_repo"/"$file"
				message="Updated - $bundle_name"
				git commit -m "$message" /tmp/"$git_repo"/"$file"
    			echo ""
    	fi
		
        else

			echo "Bundle isn't in git. Copying from current bundles to git directory"
			cp /tmp/current_bundles/"$file" /tmp/"$git_repo"/
			git add /tmp/"$git_repo"/"$file"
			message="Updated - $bundle_name"
			git commit -m "$message" /tmp/"$git_repo"/"$file"
            echo ""
		fi
	done

#Commit changes to git and push
echo "Pushing updates to Git"
echo ""
git push


# #clean up current bundle files so we don't need to worry about old bundles causing issues in the future. 
rm /tmp/current_bundles/*

echo ""
echo "Bundle backup completed " ; date
echo ""