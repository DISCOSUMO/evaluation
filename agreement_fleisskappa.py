# python agreement_fleisskappa.py ../annotation/annotations/selected_posts.withoutduplicates.txt

import sys
import re

annotationsfile = sys.argv[1]
postfeatsfile = "106long20threads.postfeats.norm.out"


# https://en.wikipedia.org/wiki/Fleiss'_kappa
def compute_fleiss_kappa (categories,votes_per_postid,n):
    # n is the number of judgments per postid
    # cats are 1 and 0 (selected and not-selected)
    # categories contains the number of occurrences of 1 and 0 in the total set of posts
    sum_assignments = 0
    for cat in categories:
        sum_assignments += categories[cat]
    Pe = 0
    for cat in categories:
        Pj = float(categories[cat])/float(sum_assignments)
        Pe += Pj*Pj

    sum_Pi = 0
    for postid in votes_per_postid:
        poscount = votes_per_postid[postid]
        negcount = n-votes_per_postid[postid]
        Pi = (1/(n*(n-1)))*(poscount*poscount+negcount*negcount-n)
        print (postid,n,poscount,negcount,Pi)
        sum_Pi += Pi

    P = sum_Pi/len(votes_per_postid)
    print (n, Pe, P)
    kappa = (P-Pe)/(1-Pe)
    return kappa


threads_per_user = dict()
selected_per_thread_and_user = dict()
usernames = dict()
threadids = dict()
utility_scores_per_thread = dict()

with open(annotationsfile,'r') as annotations:
    for line in annotations:
        columns = line.split("\t")
        name = columns[1]
        if len(columns) > 7:
            threadid = columns[7]
            selected = columns[8]
            utility = columns[10]
            threadids[threadid] = 1
            usernames[name] = 1
            threadsforuser = dict()
            if name in threads_per_user:
                threadsforuser = threads_per_user[name]
            if not threadid in threadsforuser:
                threadsforuser[threadid] = 1

                threads_per_user[name] = threadsforuser
                selected_def = dict()
                postids = selected.split(" ")
                removeatpos = dict()
                pos=0
                for postid in postids:
                    if "-" in postid:
                        removeid = re.sub("-","",postid)
                        removeatpos[removeid] = pos
                    pos += 1
                pos = 0
                for postid in postids:
                    if re.match("[1-9]+",postid):  #don't include post 0
                        if postid in removeatpos:
                            if pos > removeatpos[postid]:
                                selected_def[postid] =1
                        else :
                            selected_def[postid]=1

                selected_per_thread_and_user[(threadid,name)] = selected_def
                utility_scores = list()
                if threadid in utility_scores_per_thread:
                    utility_scores = utility_scores_per_thread[threadid]
                utility_score = utility
                if re.match('1[nao]',utility_score):
                    utility_score = 1
                utility_scores.append(int(utility_score))
                utility_scores_per_thread[threadid] = utility_scores


annotations.close()


all_postids = set()
with open(postfeatsfile,'r') as threadfeats:
    for line in threadfeats:
        columns = line.split("\t")
        threadid = columns[0]
        postid = columns[1]
        #print (line)
        all_postids.add(threadid+"_"+postid)


nrselecteds_per_postid = dict()

for (threadid,username) in selected_per_thread_and_user:
    selected_postids = selected_per_thread_and_user[(threadid,username)]
    for postid in selected_postids:
        postid = threadid+"_"+postid
        if postid in nrselecteds_per_postid:
            nrselecteds_per_postid[postid] += 1
        else:
            nrselecteds_per_postid[postid] = 1

for postid in all_postids:
    if postid not in nrselecteds_per_postid:
        nrselecteds_per_postid[postid] = 0

n=10
categories = dict()
categories[0] = 0
categories[1] = 0

for postid in all_postids:
    categories[1] += nrselecteds_per_postid[postid]
categories[0] = n*len(all_postids)-categories[1]

print (nrselecteds_per_postid)
print (len(all_postids))
print (categories[0], categories[1])


kappa = compute_fleiss_kappa(categories,nrselecteds_per_postid,n)
print(kappa)
