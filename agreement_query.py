# python agreement.py selected_posts_queries.withoutduplicates.txt

import sys
import re
import numpy



annotationsfile = sys.argv[1]

postidsfile = "postids_per_thread.queries.txt"

postids_per_thread = dict()
with open(postidsfile,'r') as postsperthread:
    threadid = ""
    for line in postsperthread:

        threadid = line.split(":")[0]
        postid = line.split(":")[1].rstrip()

        postidsforthread = list()
        if threadid in postids_per_thread:
            postidsforthread = postids_per_thread[threadid]
        postidsforthread.append(postid)
        postids_per_thread[threadid] = postidsforthread

        #print threadid, postid



threads_per_user = dict()
selected_per_thread_and_user = dict()
usernames = dict()
threadids = dict()

with open(annotationsfile,'r') as annotations:
    for line in annotations:
        columns = line.rstrip().split("\t")

        name = columns[1]
        if len(columns) > 5:
            threadid = columns[6]
            query = columns[7]
            querycounter = columns[8]
            selected = columns[9]
            relevance = int(columns[10])
            threadids[(threadid,querycounter)] = 1
            usernames[name] = 1
            threadsforuser = dict()
            if name in threads_per_user:
                threadsforuser = threads_per_user[name]
            if not (threadid,querycounter) in threadsforuser:
                threadsforuser[(threadid,querycounter)] = 1
                nrselecteds = list()

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
                    if postid != "":

                        if postid in removeatpos:
                            if pos > removeatpos[postid]:
                                selected_def[postid] =1
                           # else:
                            #    print "removed from selection: ",postid
                        else :
                            selected_def[postid]=1


                selected_per_thread_and_user[(threadid,querycounter,name)] = selected_def



annotations.close()




def compute_jaccard_index(set_1, set_2):
    if len(set_1)+len(set_2)>0:
        n = len(set_1.intersection(set_2))
        return n / float(len(set_1) + len(set_2) - n)
    else:
        return 1


def compute_kappa(list1,list2):
    #print len(list1), len(list2)
    if not len(list1) == len(list2):
        print ("Error: lists not same length: ", list1, list2)
    elif numpy.sum(list1)+numpy.sum(list2)>0:
        E1 = float(numpy.sum(list1))/float(len(list1)) * float(numpy.sum(list2))/float(len(list2))  #sum is the number of 1s
        E0 = float((len(list1)-numpy.sum(list1)))/float(len(list1)) * float((len(list2)-numpy.sum(list2)))/float(len(list2))    # len - sum is the number of 0s
        ExpAgr = E1+E0
        count_agreed = 0
        for j in range(0,len(list1)-1):
            if not list1[j]+list2[j] == 1:
                # agreed if sum is 2 or 0
                count_agreed += 1
        MeasAgr = float(count_agreed)/float(len(list1))
       # print E1, E0, ExpAgr, MeasAgr
        k = (MeasAgr-ExpAgr)/(1-ExpAgr)
        return k
    else:
        #print (list1, list2)
        return 1

sum_jaccard_over_human_pairs = 0
sum_kappa_over_human_pairs = 0
human_pairs_count = 0



kappa_sum_per_subject = dict()
jaccard_sum_per_subject = dict()
kappa_sum_per_thread = dict()
jaccard_sum_per_thread = dict()

thread_count_per_subject = dict()
pair_count_per_thread = dict()

for (threadid,querycounter) in threadids:
    set1=set()
    set2=set()
    for user1 in usernames:
        arrayofzeroesandones1 = list()

        #print threadid, user
        if (threadid,querycounter,user1) in selected_per_thread_and_user:
            selected_user1 = selected_per_thread_and_user[(threadid,querycounter,user1)]
            set1 = set(selected_user1)
            postidsforthread = postids_per_thread[threadid]
            for postid in postidsforthread:
                if postid in selected_per_thread_and_user[(threadid,querycounter,user1)]:
                    arrayofzeroesandones1.append(1)
                else:
                    arrayofzeroesandones1.append(0)

            #print threadid, user1, selected_per_thread_and_user[(threadid,querycounter,user1)], len(set1)
            #print threadid,user1, arrayofzeroesandones1, len(arrayofzeroesandones1), postcount_per_thread[threadid], numpy.sum(arrayofzeroesandones1)
        for user2 in usernames:

            if (threadid,querycounter,user2) in selected_per_thread_and_user and (threadid,querycounter,user1) in selected_per_thread_and_user:
                arrayofzeroesandones2 = list()

                if user1 != user2:# and re.match("haaaa*",user1) and re.match("haaas*",user2):
                    selected_user2 = selected_per_thread_and_user[(threadid,querycounter,user2)]
                    set2 = set(selected_user2)
                    postidsforthread = postids_per_thread[threadid]
                    for postid in postidsforthread:
                        if postid in selected_per_thread_and_user[(threadid,querycounter,user2)]:
                            arrayofzeroesandones2.append(1)
                        else:
                            arrayofzeroesandones2.append(0)


                    jaccard = compute_jaccard_index(set1,set2)
                    kappa = compute_kappa(arrayofzeroesandones1,arrayofzeroesandones2)
                    #print threadid,"\t", user1, "\t", user2, "\t", kappa

                    #print threadid, "\t", user1, "\t", selected_per_thread_and_user[(threadid,querycounter,user1)], "\t", user2, "\t", selected_per_thread_and_user[(threadid,querycounter,user2)], "\t", kappa
                    #print threadid, "\t", user1, "\t", arrayofzeroesandones1, "\t", user2, "\t", arrayofzeroesandones2, "\t", kappa
                    print (threadid,"\t",querycounter, "\t",user1,"\t",user2,"\t",jaccard,"\t",kappa)
                    human_pairs_count += 1
                    sum_jaccard_over_human_pairs += jaccard
                    sum_kappa_over_human_pairs += kappa
                    #print "HH\t", sum_kappa_over_human_pairs

                    kappa_sum_for_this_subject = 0
                    jaccard_sum_for_this_subject = 0
                    thread_count_for_this_subject = 0
                    if user2 in kappa_sum_per_subject:
                        kappa_sum_for_this_subject = kappa_sum_per_subject[user2]
                        jaccard_sum_for_this_subject = jaccard_sum_per_subject[user2]
                        thread_count_for_this_subject = thread_count_per_subject[user2]
                    kappa_sum_for_this_subject += kappa
                    jaccard_sum_for_this_subject += jaccard
                    thread_count_for_this_subject += 1

                    kappa_sum_per_subject[user2] = kappa_sum_for_this_subject
                    jaccard_sum_per_subject[user2] = jaccard_sum_for_this_subject
                    thread_count_per_subject[user2] = thread_count_for_this_subject

                    kappa_sum_for_this_thread = 0
                    jaccard_sum_for_this_thread = 0
                    pair_count_for_this_thread = 0
                    if (threadid,querycounter) in kappa_sum_per_thread:
                        kappa_sum_for_this_thread = kappa_sum_per_thread[(threadid,querycounter)]
                        jaccard_sum_for_this_thread = jaccard_sum_per_thread[(threadid,querycounter)]
                        pair_count_for_this_thread = pair_count_per_thread[(threadid,querycounter)]
                    kappa_sum_for_this_thread += kappa
                    jaccard_sum_for_this_thread += jaccard
                    pair_count_for_this_thread += 1
                    kappa_sum_per_thread[(threadid,querycounter)] = kappa_sum_for_this_thread
                    jaccard_sum_per_thread[(threadid,querycounter)] = jaccard_sum_for_this_thread
                    pair_count_per_thread[(threadid,querycounter)] = pair_count_for_this_thread

for subject in thread_count_per_subject:
    thread_count_for_this_subject = thread_count_per_subject[subject]
    kappa_sum_for_this_subject = kappa_sum_per_subject[subject]
    jaccard_sum_for_this_subject = jaccard_sum_per_subject[subject]
    avg_kappa_for_this_subject = kappa_sum_for_this_subject/float(thread_count_for_this_subject)
    avg_jaccard_for_this_subject = jaccard_sum_for_this_subject/float(thread_count_for_this_subject)
    print (subject,"\t",thread_count_for_this_subject,"\t",avg_jaccard_for_this_subject,"\t",avg_kappa_for_this_subject)

for (threadid,querycounter) in pair_count_per_thread:
    pair_count_for_this_thread = pair_count_per_thread[(threadid,querycounter)]
    kappa_sum_for_this_thread = kappa_sum_per_thread[(threadid,querycounter)]
    jaccard_sum_for_this_thread = jaccard_sum_per_thread[(threadid,querycounter)]
    avg_kappa_for_this_thread = kappa_sum_for_this_thread/float(pair_count_for_this_thread)
    avg_jaccard_for_this_thread = jaccard_sum_for_this_thread/float(pair_count_for_this_thread)
    print (threadid,"\t",querycounter,"\t",pair_count_for_this_thread,"\t",avg_jaccard_for_this_thread,"\t",avg_kappa_for_this_thread)

if human_pairs_count > 0:
    avg_jaccard_over_human_pairs = float(sum_jaccard_over_human_pairs)/float(human_pairs_count)
    avg_kappa_over_human_pairs = float(sum_kappa_over_human_pairs)/float(human_pairs_count)
    print ("mean Jaccard over human-human pairs:", avg_jaccard_over_human_pairs, "(",human_pairs_count,"human-human pairs)")
    print ("mean Kappa over human-human pairs:", avg_kappa_over_human_pairs, "(",human_pairs_count,"human-human pairs)")

