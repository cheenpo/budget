#!/usr/bin/env python

import argparse
import csv, yaml
import locale
locale.setlocale(locale.LC_ALL, '')

parser = argparse.ArgumentParser()
# mandatory
parser.add_argument("file", help="location of csv file")
# optional
parser.add_argument("-y", "--yaml", help="override default yml file (rules.yml)")
parser.add_argument("-d", "--debug", action="store_true", default=False, help="print all debugs")
args = parser.parse_args()

##
yaml_file = "rules.yml"
if args.yaml:
 yaml_file = args.yaml
f = open(yaml_file)
yaml = yaml.safe_load(f)
f.close()

##
def debug(msg):
 if args.debug:
  print "[debug] "+msg

def clean_amount(s):
 s = s.replace(",","")
 s = float(s)
 return s

def clean_account_name(name):
 for check in yaml["rename_accounts"]:
  if check["match"] in name:
  	name = check["name"]
 return name
##

##
total_positive = 0
total_negative = 0
warnings = []
skipped = []
accounts = {}
categories = {}
categories_micro = {}
unknown_details = []
##
with open(args.file) as f:
 reader = csv.reader(f)
 line = 0
 for row in reader:
  line += 1
  if line == 1:
   continue
  else:
   debug(str(row))
   status = row[0]
   description = row[2]
   amount = clean_amount(row[6])
   account = row[10]
   #
   if status != yaml["status_to_analyze"]:
    skipped.append(status+" : "+description+" : "+str(amount))
    continue
   else:
   	# add to totals
    if amount < 0:
     total_negative += amount
    else:
     total_positive += amount

    # add to account
    if account in accounts:
     accounts[account] += amount
    else:
     accounts[account] = amount

    # categorize
    category = "unknown"
    category_micro = "unknown"
    for check in yaml["categories"]:
     if check["match"] in description:
      category = check["macro"]
      category_micro = check["macro"]+"."+check["micro"]
      break
    if category in categories:
     categories[category] += amount
    else:
     categories[category] = amount
    if category_micro in categories_micro:
     categories_micro[category_micro] += amount
    else:
     categories_micro[category_micro] = amount
    if category == "unknown":
     unknown_details.append(description)
    if abs(amount) > yaml["global_warning_amount"]:
     warnings.append(category+ " above global_warning_amount: abs("+str(amount)+") > "+str(yaml["global_warning_amount"])+" : "+description)
    debug("category: "+category)


## see if there are any warnings
for category in categories_micro:
 for check in yaml["warnings"]:
  if check["category"] == category:
   if "lower_limit" in check and abs(categories_micro[category]) < check["lower_limit"]:
     warnings.append(category+ " below lower_limit: abs("+str(categories_micro[category])+") < "+str(check["upper_limit"]))
   else:
    if abs(categories_micro[category]) > check["upper_limit"]:
     warnings.append(category+ " above upper_limit: abs("+str(categories_micro[category])+") > "+str(check["upper_limit"]))

##
print "summary..."
print " total_positive: "+locale.currency(total_positive, grouping=True)
print " total_negative: "+locale.currency(total_negative, grouping=True)
total = (total_positive+total_negative)
print " total: "+locale.currency(total, grouping=True)
if "income" in categories:
 import math
 print ""
 print " income: "+locale.currency(categories["income"], grouping=True)
 print " percentage of income: "+str(math.ceil((total/categories["income"])*10000)/100)+"%"

print ""
print "skipped ("+str(len(skipped))+")..."
for v in sorted(skipped):
 print v
print ""
print "warnings ("+str(len(warnings))+")..."
if len(warnings) > 0:
 for warning in sorted(warnings):
  print warning
else:
 print "none"
print ""
print "accounts ("+str(len(accounts))+")..."
for account in sorted(accounts):
 print " "+clean_account_name(account)+": "+locale.currency(accounts[account], grouping=True)
print ""
print "categories (macro) ("+str(len(categories))+")..."
for category in sorted(categories):
 print " "+category+": "+locale.currency(categories[category], grouping=True)
print ""
print "categories (micro) ("+str(len(categories_micro))+")..."
for category in sorted(categories_micro):
 print " "+category+": "+locale.currency(categories_micro[category], grouping=True)
##

debug("\nunknown descriptions...")
for detail in sorted(unknown_details):
 debug(detail)
debug(str(line)+" lines in file")
debug(str(len(unknown_details))+" unknowns")
##
debug("all done.")
