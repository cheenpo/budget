# budget

so after kicking mint.com to the curb and trying to go cold turkey on being ocd about money stuff... I tinkered with this.

## the idea

to simply download a csv export of all the transactions from citibank and run them through a simple script to categorize everything.

## how it works

run the python script with the path to the csv export (usually/default named 'ExportData.csv')
the script will pick up the rules in the yml file (rules.yml) to categorize... because what fun is it to trust the banks categories... >:)
does a generic total, macro category total, micro category total, any odd-balls, etc...

## get started

peek at rules.yml.example, modify, and strip off the ".example"... or just make and point to your own yml file
run the script and point to what you need to

