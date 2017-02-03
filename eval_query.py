# eval_query.py ../summarization/viva_queries.postselection.baseline.out "baseline" ../annotation/annotations/selected_posts_queries.withoutduplicates.txt
# eval_query.py ../summarization/viva_queries.postselection.oracle.out "oracle" ../annotation/annotations/selected_posts_queries.withoutduplicates.txt


import operator

import sys

import re
import numpy

predictionsfile = sys.argv[1]
methodname = sys.argv[2]
annotationsfile = sys.argv[3]

threadfeatsfile = "106long20threads.threadfeats.out" # for postcount per thread

models = dict()
models[methodname] = 1

def get_predictions_from_predictionsfile (predictionsfile,method):
    ranked_postids_per_thread = dict()
    with open(predictionsfile,'r') as predictions:
        posts_with_predicted_value_per_thread = dict()
        for line in predictions:
            threadid,query,postid,predicted = line.rstrip().split('\t')
            #print (threadid,query,postid,predicted)
            posts_with_predicted_value = dict()
            if (threadid,query) in posts_with_predicted_value_per_thread:
                posts_with_predicted_value = posts_with_predicted_value_per_thread[(threadid,query)]
            posts_with_predicted_value[postid] = float(predicted)
            posts_with_predicted_value_per_thread[(threadid,query)] = posts_with_predicted_value

        for (threadid,query) in posts_with_predicted_value_per_thread:
            posts_with_predicted_value = posts_with_predicted_value_per_thread[(threadid,query)]
            sorted_postids_tuples = sorted(posts_with_predicted_value.items(), key=operator.itemgetter(1), reverse=True)
            #print (threadid)
            sorted_postids = list()
            for (postid,score) in sorted_postids_tuples:
                #print (postid,score)
                sorted_postids.append(postid)
            ranked_postids_per_thread[(threadid,query)] = sorted_postids
            #for postid in sorted_postids:
                #print (postid,posts_with_predicted_value[postid])
            print (method, threadid, ranked_postids_per_thread[(threadid,query)],sep='\t')
        predictions.close()

    return ranked_postids_per_thread

threadids = dict()
threadids_querycounters = dict()
usernames = dict()
queries = dict()
querycounters = dict()

def get_human_selected_from_annotationsfile (annotationsfile):

    global threadids
    global usernames
    global queries
    global querycounters
    threadsqueries_per_user = dict()
    selected_per_thread_and_user = dict()
    relevance_scores_per_thread_query = dict()
    relevance_per_thread_query_user = dict()

    with open(annotationsfile,'r') as annotations:
        for line in annotations:
            columns = line.split("\t")
            name = columns[1]
            if len(columns) > 7:
                threadid = columns[6]
                query = columns[7].lower()
                querycounter = columns[8]
                selected = columns[9]
                relevance = columns[10]
                threadids[threadid] = 1
                threadids_querycounters[(threadid,querycounter)] = 1
                usernames[name] = 1
                threadsqueriesforuser = dict()
                if name in threadsqueries_per_user:
                    threadsqueriesforuser = threadsqueries_per_user[(name,querycounter)]
                if not (name,querycounter) in threadsqueriesforuser:
                    threadsqueriesforuser[(name,querycounter)] = 1
                    nrselecteds = list()

                    threadsqueries_per_user[(name,querycounter)] = threadsqueriesforuser
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

                    selected_per_thread_and_user[(threadid,querycounter,name)] = selected_def
                    relevance_scores = []
                    if (threadid,querycounter) in relevance_scores_per_thread_query:
                        relevance_scores = relevance_scores_per_thread_query[(threadid,querycounter)]
                    relevance_scores.append(relevance)
                    relevance_scores_per_thread_query[(threadid,querycounter)] = relevance_scores
                    relevance_per_thread_query_user[(threadid,querycounter,name)] = relevance
                    queries[(threadid,querycounter)] = query
                    querycounters[(threadid,query)] = querycounter
                    #print (threadid,query,querycounter)


    annotations.close()

    return threadsqueries_per_user, selected_per_thread_and_user


def get_postcount_per_thread (threadfeatsfile):
    postcount_per_thread = dict()
    with open(threadfeatsfile,'r') as threadfeats:
        for line in threadfeats:
            columns = line.split("\t")
            threadid = columns[0]
            postcount_cutoff = columns[2]
            if re.match("[0-9]",postcount_cutoff):
                postcount_per_thread[threadid] = int(postcount_cutoff)
    return postcount_per_thread


def compute_jaccard_index(set_1, set_2):
    if len(set_1)+len(set_2)>0:
        n = len(set_1.intersection(set_2))
        return n / float(len(set_1) + len(set_2) - n)
    else:
        return 1

def compute_precision(model,reference):
    if len(model)+len(reference)>0:
        tp=len(model.intersection(reference))
        fp=len(model-reference)
        if tp > 0:
            return float(tp)/(float(fp)+float(tp))
        else:
            return 0
    else:
        return 1

def compute_recall(model,reference):
    if len(model)+len(reference)>0:
        tp=len(model.intersection(reference))
        fn=len(reference-model)
        if tp > 0:
            return float(tp)/(float(fn)+float(tp))
        else:
            return 0
    else:
        return 1

def compute_kappa(list1,list2):
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
        #print E1, E0, ExpAgr, MeasAgr
        k = (MeasAgr-ExpAgr)/(1-ExpAgr)
        return k
    else:
        return 1




'''
MAIN
'''

threadsqueries_per_user, selected_per_thread_and_user = get_human_selected_from_annotationsfile(annotationsfile)
postcount_per_thread = get_postcount_per_thread(threadfeatsfile)


#print (models)
#print (usernames)

for method in models:
    print ("METHOD:",method)

    ranked_postids_per_threadquery = get_predictions_from_predictionsfile(predictionsfile,method)

    ranked_postids_per_threadquerycounter = dict()
    for (threadid,querycounter) in ranked_postids_per_threadquery:
        #print (threadid,querycounter,ranked_postids_per_threadquery[(threadid,querycounter)])
        if re.match(".*[a-z].*",querycounter):
            # query instead of querycounter
            query = querycounter
            real_querycounter = querycounters[(threadid,query)]
            ranked_postids_per_threadquerycounter[(threadid,real_querycounter)] = ranked_postids_per_threadquery[(threadid,query)]

    ranked_postids_per_threadquery = ranked_postids_per_threadquerycounter
    for cutoff in range (1,20):
        for (threadid,querycounter) in ranked_postids_per_threadquery:
            ranked_postids = ranked_postids_per_threadquery[(threadid,querycounter)]
            #print (threadid,querycounter,ranked_postids)
            selectedposts = dict()
            k=0
            for postid in ranked_postids:
                k +=1
                if k <= cutoff:
                    selectedposts[postid] = 1
            selected_per_thread_and_user[(threadid,querycounter,method)] = selectedposts
            #print (cutoff,threadid,querycounter,selectedposts)
        #sum_precision,sum_recall,human_model_pairs_count = evaluate(threadids_querycounters,method)
        true_set_per_rater_over_all_threads = dict() # key is username, value is set of threadid_querycounter_selectedpostids
        selected_set_by_model_per_rater = dict() # key is username, value set of threadid_querycounter_selectedpostids by model, for all thread-queries that are common with the user

        sum_precision,sum_recall,human_model_pairs_count = 0,0,0
        number_of_threadsqueries_per_rater = dict()

        for (threadid,querycounter,username) in selected_per_thread_and_user:
            if username == method:

                for (threadid2,querycounter2,username2) in selected_per_thread_and_user:
                    if username2 != method and threadid == threadid2 and querycounter == querycounter2:
                        #print (threadid2,querycounter2,username2)

                        # collect sets of selected units for model and this user
                        #print (method,username2,threadid,querycounter,selected_per_thread_and_user[(threadid,querycounter,username)],selected_per_thread_and_user[(threadid2,querycounter2,username2)] )
                        for postid in selected_per_thread_and_user[(threadid2,querycounter2,username2)]:
                            selected_item = threadid2+"_"+querycounter2+"_"+postid
                            true_set_for_this_rater = set()
                            if username2 in true_set_per_rater_over_all_threads:
                                true_set_for_this_rater = true_set_per_rater_over_all_threads[username2]
                            true_set_for_this_rater.add(selected_item)
                            true_set_per_rater_over_all_threads[username2] = true_set_for_this_rater

                        for postid in selected_per_thread_and_user[(threadid,querycounter,method)]:
                            selected_item = threadid+"_"+querycounter+"_"+postid
                            selected_set_by_model_for_this_rater = set()
                            if username2 in selected_set_by_model_per_rater:
                                selected_set_by_model_for_this_rater = selected_set_by_model_per_rater[username2]
                            selected_set_by_model_for_this_rater.add(selected_item)
                            selected_set_by_model_per_rater[username2] = selected_set_by_model_for_this_rater

                        number_of_threadsqueries_for_this_rater = 0
                        if username2 in number_of_threadsqueries_per_rater:
                            number_of_threadsqueries_for_this_rater += 1
                        else:
                            number_of_threadsqueries_for_this_rater = 1
                        #print(username2,threadid,querycounter,number_of_threadsqueries_for_this_rater)
                        number_of_threadsqueries_per_rater[username2] = number_of_threadsqueries_for_this_rater


        for rater in true_set_per_rater_over_all_threads:
            true_set_for_this_rater = true_set_per_rater_over_all_threads[rater]
            selected_set_by_model_for_this_rater = selected_set_by_model_per_rater[rater]
            precision = compute_precision(selected_set_by_model_for_this_rater,true_set_for_this_rater)
            recall = compute_recall(selected_set_by_model_for_this_rater,true_set_for_this_rater)

            number_of_threadsqueries_for_this_rater = number_of_threadsqueries_per_rater[rater]
            human_model_pairs_count += number_of_threadsqueries_for_this_rater # weighted average

            sum_precision += number_of_threadsqueries_for_this_rater*precision
            sum_recall += number_of_threadsqueries_for_this_rater*recall
            #print (rater,method,number_of_threadsqueries_for_this_rater,precision,recall,)



        avg_precision = float(sum_precision)/float(human_model_pairs_count)
        avg_recall = float(sum_recall)/float(human_model_pairs_count)
        avg_f1 = 2*(avg_precision*avg_recall)/(avg_precision+avg_recall)
        print (method,"\t",cutoff,"\t",avg_recall, "\t", avg_precision, "\t", avg_f1)
