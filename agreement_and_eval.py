# python agreement_and_eval.py ../annotation/annotations/selected_posts.withoutduplicates.txt ../annotation/annotations/test_all_with_predictions.normfeats.txt

import sys
import re
import os
import xml.etree.ElementTree as ET

import numpy
from random import randint

annotationsfile = sys.argv[1]
predictionsfile = sys.argv[2]
personalizedname = ""
if len(sys.argv)>3:
    personalizedname = sys.argv[3]

treadfeatsfile = "106long20threads.threadfeats.out"

postcount_per_thread = dict()
with open(treadfeatsfile,'r') as threadfeats:
    for line in threadfeats:
        columns = line.split("\t")
        threadid = columns[0]
        postcount_cutoff = columns[2]
        if re.match("[0-9]",postcount_cutoff):
            postcount_per_thread[threadid] = int(postcount_cutoff)

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

if len(personalizedname) > 0:
    usernames.clear()
    usernames[personalizedname] =1

usernames["MODEL"] = 1
#print usernames

postlengths = dict()
with open(predictionsfile,'r') as predictions:
    name = "MODEL"
    for line in predictions:
        #threadid	postid	abspos	relpos	noresponses	cosinesimwthread	cosinesimwtitle	wordcount	uniquewordcount	ttr	relpunctcount	avgwordlength	avgsentlength	relauthorcountsinthread	nrofvotes	predicted	NORM_selectedbasedonthreshold
        columns = line.split("\t")
        threadid = columns[0]
        postid = columns[1]
        wordcount = columns[7]
        postlengths_for_thread = dict()
        if threadid in postlengths:
            postlengths_for_thread = postlengths[threadid]
        if re.match("[-0-9]+",wordcount):
            postlengths_for_thread[postid] = float(wordcount)
        postlengths[threadid] = postlengths_for_thread
        selected = columns[-1].rstrip()
        #print threadid, postid, selected
        selectedposts = dict()
        if (threadid,name) in selected_per_thread_and_user:
            selectedposts = selected_per_thread_and_user[(threadid,name)]
        if selected is "1":
            selectedposts[postid] =1
        selected_per_thread_and_user[(threadid,name)] = selectedposts
            #print threadid, name, postid

predictions.close()

#print "\nRandom post selection"
usernames["RANDOM"] = 1
name = "RANDOM"
for threadid in threadids:
    remaining_postids = list()
    remaining_postids.extend(range(1, postcount_per_thread[threadid]))
    #print remaining_postids
    selectedposts = dict()
    for j in range(0,7):
        # pick 7 random posts

        r = randint(0,len(remaining_postids)-1)

        pickedpost = remaining_postids[r]
        #print threadid, r, pickedpost
        del remaining_postids[r]
        selectedposts[str(pickedpost)] = 1
    #pickedposts.sort()
    selected_per_thread_and_user[(threadid,name)] = selectedposts

usernames["POSITION"] = 1
name = "POSITION"
for threadid in threadids:
    selectedposts = dict()
    for j in range(1,8):
        selectedposts[str(j)] = 1
    selected_per_thread_and_user[(threadid,name)] = selectedposts
    #print threadid, "POSITION", selectedposts

usernames["LENGTH"] = 1
name = "LENGTH"
for threadid in threadids:
    #print ""
    postlengths_for_thread = postlengths[threadid]
    j = 0
    selectedposts = dict()
    for postid, length in sorted(postlengths_for_thread.items(), key=lambda x: (-x[1], x[0])):
        #print threadid, postid, length
        selectedposts[postid] = 1
        if j >= 7:
            break
        j += 1
    selected_per_thread_and_user[(threadid,name)] = selectedposts
    #print threadid, "LENGTH", selectedposts

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

def tokenize(t):
    text = t.lower()
    text = re.sub("\n"," ",text)
    text = re.sub('[^a-zèéeêëûüùôöòóœøîïíàáâäæãåA-Z0-9- \']', "", text)
    wrds = text.split()
    return wrds



def get_all_ngrams (text,n) :
    words = tokenize(text)
    i=0
    terms = dict()
    for word in words :
        if n == 1:
            if word in terms :
                terms[word] += 1
            else :
                terms[word] = 1
        elif n == 2 :
            if i< len(words)-1 :
                bigram = words[i]+ " " +words[i+1]
                if bigram in terms :
                    terms[bigram] += 1
                else :
                    terms[bigram] = 1

        i += 1
    return terms


'''
http://codereview.stackexchange.com/questions/20337/find-the-longest-common-subsequence-algorithm-low-speed
X=A, B, C, B, D, A, B‬‬
‫‪Y=B, D, C, A, B, A‬‬
1. Pick A in the first string.
2. Look for A in Y.
3. Now that there is an A in the second string, append it to common_subsequence.
4. Return to the first string and pick the next letter that is B.
5. Look for B in the second string this time starting from the position of A.
6. There is a B after A so append B to common_subsequence.
7. Now pick the next letter in the first string that is C. There isn't a C next to B in the second string.
  So assign the value of common_subsequence to lcs because its length is greater than the length of lcs.
Repeat the previous steps until reaching the end of the first string. In the end the value of lcs is the Longest Common Subsequence.
'''

def get_lcs(text_m,text_r):
    if not (text_m and text_r): return # if string is empty
    words_m = tokenize(text_m)
    words_r = tokenize(text_r)
    lcs = [] #  longest common subsequences
    lcslen = 0 # length of longest common subsequence so far
    #print ("model",words_m)
    #print ("reference",words_r)
    for i in range(0,len(words_m)):
        cs = [] # common subsequence
        start = 0 # start position in text_r
        for item in words_m[i:]:
            if item in words_r[start:]:
                index = words_r.index(item, start) # position of the common word
                #cs.append(item) # add common word to the cs
                cs.append(index) # instead of word, add the index of the word in the reference post
                # (needed for the union LCS)
                start = index + 1
                if index == len(words_r) - 1: break # if reached to the end of text_r
        # updates lcs and lcslen if found better cs
        if len(cs) > lcslen: lcs, lcslen = [cs], len(cs)
        elif len(cs) == lcslen: lcs.append(cs)
    return lcs, lcslen

#print (lcs,lcslen)


def compute_rouge_l(threadid,name,list_model,list_reference):
    # http://anthology.aclweb.org/W/W04/W04-1013.pdf (section 3.2)
    if len(list_model)==len(list_reference)==0:
        print (threadid,name,1.0,1.0,1.0)
        return 1.0,1.0,1.0
    if len(list_model)==0:
        print (threadid,name,0.0,0.0,0.0)
        return 0.0,0.0,0.0
    if len(list_reference) == 0:
        print (threadid,name,0.0,0.0,0.0)
        return 0.0,0.0,0.0
    sum_of_lcs = 0
    length_reference = 0
    length_model = 0
    for postid_m in list_reference:
        length_model += len(content_of_posts[(threadid,postid_m)])
    for postid_r in list_model:
        union_lcs = set()
        length_reference += len(content_of_posts[(threadid,postid_r)])
        for postid_m in list_reference:
            # 'candidate sentences'
            lcss,lcslen = get_lcs(content_of_posts[(threadid,postid_m)],content_of_posts[(threadid,postid_r)])
            #print (lcslen,lcss)
            # the function returns an array of lcss, all lcss that have the same (maximum) length
            for lcs in lcss:
                # each lcs is not a list of indices of the words in the reference post that occur in the lcs of the current candidate
                #print ("-",threadid,postid_r,postid_m,lcslen,lcs)
                for index_of_word in lcs:
                    union_lcs.add(index_of_word)
        sum_of_lcs += len(union_lcs)
        #print("UNION",threadid,postid_r,len(union_lcs),union_lcs)
    recall_lcs = float(sum_of_lcs)/float(length_reference)
    precision_lcs = float(sum_of_lcs)/float(length_model)
    if recall_lcs+precision_lcs==0:
        return 0.0,0.0,0.0
        print (threadid,name,0.0,0.0,0.0)
    F1_lcs = 2*(recall_lcs*precision_lcs)/(recall_lcs+precision_lcs)
    #print(sum_of_lcs,length_reference,length_model)
    print (threadid,name,recall_lcs,precision_lcs,F1_lcs)
    return recall_lcs,precision_lcs,F1_lcs


def compute_rouge_n(model,reference,n):
    # model and reference are both strings: concatenations of the selected posts by the model and by the human
    ngrams_model = get_all_ngrams(model,n)
    ngrams_reference = get_all_ngrams(reference,n)
    #print (threadid,postid,ngrams_reference)
    overlapping = 0
    for ngram_m in ngrams_model:
        for ngram_r in ngrams_reference:
            if ngram_m == ngram_r:
                overlapping += 1
    if len(ngrams_model) == len(ngrams_reference) == 0:
        rouge = 1
    elif len(ngrams_reference) == 0:
        rouge = 0
    else:
        rouge = float(overlapping)/float(len(ngrams_reference))
    return rouge


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



kappa_sum_per_subject = dict()
jaccard_sum_per_subject = dict()
thread_count_per_subject = dict()

models = dict()
models["MODEL"] = 1
models["RANDOM"] = 1
models["POSITION"] = 1
models["LENGTH"] = 1

sum_length_of_posts = 0
total_no_of_posts = 0
# get content of all posts (needed for ROUGE)
content_of_posts = dict() # key is (threadid,postid), value is textual content of post
rootdir = "../dataconversion/Viva_forum/samples/106long20threads"
for f in os.listdir(rootdir):
    if f.endswith("xml"):

        postids = list()
        termvectors = dict()  # key is postid, value is dict with term -> termcount for post
        termvectorforthread = dict()  # key is term, value is termcount for full thread
        termvectorfortitle = dict()  # key is term, value is termcount for title
        authorcountsinthread = dict()  # key is authorid, value is number of posts by author in this thread

        tree = ET.parse(rootdir+"/"+f)
        root = tree.getroot()

        for thread in root:
            threadid = thread.get('id')
            category = thread.find('category').text

            title = thread.find('title').text


        for posts in thread.findall('posts'):
            noofposts = len(posts.findall('post'))
            if noofposts > 50:
                noofposts = 50
            postcount = 0

            #print time.clock(), "\t", "extract feats from each post"

            for post in posts.findall('post'):
                postcount += 1
                postid = post.get('id')

                if 1 < postcount <= 51:
                    # don't include opening post in feature set
                    # and include at most 50 responses


                    body = post.find('body').text
                    if postcount > 51:
                        continue
                    elif postid=="0":
                        continue
                    elif body is None:
                        body = ""
                    content_of_posts[(threadid,postid)] = body
                    words = tokenize(body)
                    sum_length_of_posts += len(words)
                    total_no_of_posts += 1


sum_jaccard_over_human_pairs = 0
sum_kappa_over_human_pairs = 0
human_pairs_count = 0

sum_jaccard_over_human_model_pairs = 0
sum_kappa_over_human_model_pairs = 0
human_model_pairs_count = 0
human_model_pairs_count_modelnonzero = 0

sum_precision = 0
sum_recall = 0
sum_f1 = 0
sum_rouge1 = 0
sum_rouge2 = 0
sum_rouge_l_precision = 0
sum_rouge_l_recall = 0
sum_rouge_l_F1 = 0
sum_length_of_summaries_model = 0
sum_length_of_summaries_reference = 0

for threadid in threadids:
    medianutil = numpy.median(utility_scores_per_thread[threadid])
    set1=set()
    set2=set()
    for user1 in usernames:
        arrayofzeroesandones1 = list()

        #print threadid, user
        if (threadid,user1) in selected_per_thread_and_user:
            selected_user1 = selected_per_thread_and_user[(threadid,user1)].keys()
            set1 = set(selected_user1)
            for i in range(1,postcount_per_thread[threadid]+1):
                if str(i) in selected_per_thread_and_user[(threadid,user1)].keys():
                    arrayofzeroesandones1.append(1)
                else:
                    arrayofzeroesandones1.append(0)
            #print threadid, user1, selected_per_thread_and_user[(threadid,user1)], len(set1)
            #print threadid,user1, arrayofzeroesandones1, len(arrayofzeroesandones1), postcount_per_thread[threadid], numpy.sum(arrayofzeroesandones1)
        for user2 in usernames:

            if (threadid,user2) in selected_per_thread_and_user and (threadid,user1) in selected_per_thread_and_user:
                arrayofzeroesandones2 = list()

                if user1 is not user2:
                    selected_user2 = selected_per_thread_and_user[(threadid,user2)].keys()
                    set2 = set(selected_user2)
                    for i in range(1,postcount_per_thread[threadid]+1):
                        if str(i) in selected_per_thread_and_user[(threadid,user2)].keys():
                            arrayofzeroesandones2.append(1)
                        else:
                            arrayofzeroesandones2.append(0)

                    jaccard = compute_jaccard_index(set1,set2)
                    kappa = compute_kappa(arrayofzeroesandones1,arrayofzeroesandones2)
                    #print threadid,"\t", user1, "\t", user2, "\t", kappa

                    #if threadid == "220912" and user2 == "Ida Boesten" and user1 == "POSITION":
                    #print threadid, "\t", user1, "\t", selected_per_thread_and_user[(threadid,user1)], "\t", user2, "\t", selected_per_thread_and_user[(threadid,user2)], "\t", kappa


                    if user1 not in models and user2 not in models:
                        human_pairs_count += 1
                        sum_jaccard_over_human_pairs += jaccard
                        sum_kappa_over_human_pairs += kappa
                        #print "HH\t", sum_kappa_over_human_pairs
                    else:
                        # one of two is model
                        #print "HM\t", sum_kappa_over_human_model_pairs
                        precision=0
                        recall=0
                        rouge=0
                        selected_content_user1 = ""
                        for postid in set1:
                            selected_content_user1 += " "+content_of_posts[(threadid,postid)]
                        
                        selected_content_user2 = ""
                        for postid in set2:
                            selected_content_user2 += " "+content_of_posts[(threadid,postid)]

                        #if user1 is "RANDOM"  and user2 not in models:
                        #if user1 is "POSITION" and user2 not in models:
                        if user1 is "LENGTH"  and user2 not in models:

                            #if jaccard <0:
                            #print threadid, user1, user2, jaccard,"\t", kappa
                        #if user1 is "MODEL"  and user2 not in models:
                            print (threadid,user1,user2)
                            sum_jaccard_over_human_model_pairs += jaccard
                            sum_kappa_over_human_model_pairs += kappa

                            human_model_pairs_count +=1

                            precision = compute_precision(set1,set2)
                            recall = compute_recall(set1,set2)

                            rouge1 = compute_rouge_n(selected_content_user1,selected_content_user2,1)
                            rouge2 = compute_rouge_n(selected_content_user1,selected_content_user2,2)

                            words_user1 = tokenize(selected_content_user1)
                            words_user2 = tokenize(selected_content_user2)

                            sum_length_of_summaries_model += len(words_user1)
                            sum_length_of_summaries_reference += len(words_user2)


                            recall_lcs,precision_lcs,F1_lcs = compute_rouge_l(threadid,user2,set1,set2)

                            if len(set1) > 0:
                                human_model_pairs_count_modelnonzero += 1

                            #else:
                            #print threadid, medianutil, user1, set1, user2, set2

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

                        #else:
                        #    precision = compute_precision(set2,set1)
                        #    recall = compute_recall(set2,set1)
                        #    if len(set2) > 0:
                        #        human_model_pairs_count_modelnonzero += 1
                            #else:
                                #print threadid, medianutil, user1, set1, user2, set2
                            f1 =0
                            if precision + recall > 0:
                                f1 = 2*(precision*recall)/(precision+recall)
                            #print threadid, "\t", precision, "\t",recall,"\t",f1
                            sum_precision += precision
                            sum_recall += recall
                            sum_f1 += f1
                            sum_rouge1 += rouge1
                            sum_rouge2 += rouge2
                            sum_rouge_l_precision += precision_lcs
                            sum_rouge_l_recall += recall_lcs
                            sum_rouge_l_F1 += F1_lcs


for subject in thread_count_per_subject:
    thread_count_for_this_subject = thread_count_per_subject[subject]
    kappa_sum_for_this_subject = kappa_sum_per_subject[subject]
    jaccard_sum_for_this_subject = jaccard_sum_per_subject[subject]
    avg_kappa_for_this_subject = kappa_sum_for_this_subject/float(thread_count_for_this_subject)
    avg_jaccard_for_this_subject = jaccard_sum_for_this_subject/float(thread_count_for_this_subject)
    print (subject,"\t",thread_count_for_this_subject,"\t",avg_jaccard_for_this_subject,"\t",avg_kappa_for_this_subject)


if human_pairs_count > 0:
    avg_jaccard_over_human_pairs = float(sum_jaccard_over_human_pairs)/float(human_pairs_count)
    avg_kappa_over_human_pairs = float(sum_kappa_over_human_pairs)/float(human_pairs_count)
    print ("mean Jaccard over human-human pairs:", avg_jaccard_over_human_pairs, "(",human_pairs_count,"human-human pairs)")
    print ("mean Kappa over human-human pairs:", avg_kappa_over_human_pairs, "(",human_pairs_count,"human-human pairs)")

avg_jaccard_over_human_model_pairs = float(sum_jaccard_over_human_model_pairs)/float(human_model_pairs_count)
avg_kappa_over_human_model_pairs = float(sum_kappa_over_human_model_pairs)/float(human_model_pairs_count)
avg_precision = float(sum_precision)/float(human_model_pairs_count)
avg_recall = float(sum_recall)/float(human_model_pairs_count)
avg_f1 = 2*(avg_precision*avg_recall)/(avg_precision+avg_recall)
avg_rouge1 = float(sum_rouge1)/float(human_model_pairs_count)
avg_rouge2 = float(sum_rouge2)/float(human_model_pairs_count)
avg_rouge_l_precision = float(sum_rouge_l_precision)/float(human_model_pairs_count)
avg_rouge_l_recall = float(sum_rouge_l_recall)/float(human_model_pairs_count)
#avg_rouge_l_F1 = float(sum_rouge_l_F1)/float(human_model_pairs_count)
avg_rouge_l_F1_overall = 2*(avg_rouge_l_precision*avg_rouge_l_recall)/(avg_rouge_l_precision+avg_rouge_l_recall)
avg_length_model = float(sum_length_of_summaries_model)/float(human_model_pairs_count)
avg_length_reference = float(sum_length_of_summaries_reference)/float(human_model_pairs_count)
avg_length_posts = float(sum_length_of_posts)/float(total_no_of_posts)

print ("mean Jaccard over human-model pairs:", avg_jaccard_over_human_model_pairs, "(",human_model_pairs_count,"human-model pairs)")
print ("mean Kappa over human-model pairs:", avg_kappa_over_human_model_pairs, "(",human_model_pairs_count,"human-model pairs)")
print ("mean precision (macro avg over threads):\t",avg_precision, "\tmean recall (macro avg over threads):\t", avg_recall, "\tmean f1 (macro avg over threads):\t", avg_f1, "\t(",human_model_pairs_count,"human-model pairs)")
print ("mean ROUGE-1 over human-model pairs:", avg_rouge1, "(",human_model_pairs_count,"human-model pairs)")
print ("mean ROUGE-2 over human-model pairs:", avg_rouge2, "(",human_model_pairs_count,"human-model pairs)")
print ("mean ROUGE-L Precision over human-model pairs:", avg_rouge_l_precision, "(",human_model_pairs_count,"human-model pairs)")
print ("mean ROUGE-L Recall over human-model pairs:", avg_rouge_l_recall, "(",human_model_pairs_count,"human-model pairs)")
#print ("mean ROUGE-L F1 over human-model pairs:", avg_rouge_l_F1, "(",human_model_pairs_count,"human-model pairs)")
print ("mean ROUGE-L F1 overall over human-model pairs:", avg_rouge_l_F1_overall, "(",human_model_pairs_count,"human-model pairs)")
print ("mean length of model summary:", avg_length_model, "(",human_model_pairs_count,"human-model pairs)")
print ("mean length of reference summary:", avg_length_reference, "(",human_model_pairs_count,"human-model pairs)")
print ("mean length of post:", avg_length_posts)