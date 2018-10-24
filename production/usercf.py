import math
import sys
sys.path.append("../util")
import reader
import operator
import pickle

def transfer_user_click(user_click):
    item_click={}
    for user in user_click:
        click_list = user_click[user]
        for item in click_list:
            if item not in item_click:
                item_click[item] = []
            item_click[item].append(user)
    return item_click
def base_contribute_value():
    return 1
def update_contribute_value(item_click_count):
    return 1/(1+math.log10(1+item_click_count))

def update_contribute_value(click_time1,click_time2):
    dif = abs(int(click_time1)-click_time2)
    dif = dif/(60*60*24)
    return 1/(1+dif)

def cal_user_sim(item_click_by_user,user_click_log):
    user_co_appear={}
    user_sim={}
    user_sim_sorted ={}
    user_click_times={} 
    '''记录每一个user，有多少点击'''
    for itemid ,userlist in item_click_by_user.items():
        '''userlist = item_click_by_user[itemid]'''
        inum = len(userlist)
        '''
        inum:itemid被多少了用户点击了 
        '''
        for i in range(0,len(userlist)):
            user_i = userlist[i]
            user_co_appear.setdefault(user_i,{})
            if user_i not in user_click_times:
                user_click_times.setdefault(user_i,0)
            user_click_times[user_i]+=1
            for j in range(i+1,len(userlist)):
                user_j = userlist[j]
                user_co_appear.setdefault(user_j,{})
                if user_j  not in user_co_appear[user_i]:
                    user_co_appear[user_i].setdefault(user_j,0)
                click_time1 = user_click_log[user_i+"_"+itemid]
                click_time2 = user_click_log[user_j+"_"+itemid]
                user_co_appear[user_i][user_j]+=update_two_contribute_value(click_time1,click_time2)
                #user_co_appear[user_i][user_j]+=update_contribute_value(inum))
                if user_i not in user_co_appear[user_j]:
                    user_co_appear[user_j].setdefault(user_i,0)
                user_co_appear[user_j][user_i]+=update_two_contribute_value(click_time1,click_time2)
                #user_co_appear[user_j][user_i]+=update_contribute_value(inum))

    for user_i,user_i_co in user_co_appear.items():
        user_sim.setdefault(user_i,{})
        for  user_j , co_times in user_i_co.items():
            user_sim[user_i][user_j] = co_times/math.sqrt(user_click_times[user_i]*user_click_times[user_j])
    for user_i ,items in user_sim.items():
        user_sim_sorted[user_i] = sorted(items.items(),key=operator.itemgetter(1),reverse=True)
    return user_sim_sorted

def cal_recom_result(user_click,user_sim):
    recom_result = {}
    topK = 5
    itemK = 3
    recom_result_sorted = {}
    for user_i,itemlist in user_click.items():
        recom_result.setdefault(user_i,{})
        for zuhe in user_sim[user_i][:topK]:
            user_j = zuhe[0]
            score = zuhe[1]
            for itemj in user_click[user_j][:itemK]:
                recom_result[user_i][itemj] = score
        recom_result_sorted[user_i] = sorted(recom_result[user_i].items(),key=operator.itemgetter(1),reverse=True)
    return recom_result_sorted
def debug_user_sim(user_sim):
    fixed_user = "1"
    topk = 5
    for zuhe in user_sim[fixed_user][:topk]:
        itemid,score = zuhe
        print("id: %s,score: %f" % (itemid,score))
    
def debug_recom_result(recom_result,item_info):
    fixed_user = "1"
    for zuhe in recom_result[fixed_user]: 
        itemid,score = zuhe
        print("movie title: %s ,genres:%s ,score:%f" %(item_info[itemid][0],item_info[itemid][1],score))

def main_flow():
    user_click,user_click_time = reader.get_user_click("../ml-1m/ratings.dat")
    item_info = reader.get_item_info("../ml-1m/movies.dat")
    item_click_by_user = transfer_user_click(user_click)
    
    '''
    with open("user.pkl","rb") as fp:
        user_sim = pickle.load(fp) 
    '''
    user_sim = cal_user_sim(item_click_by_user,user_click_time)
    print(user_sim["1"])
    with open("user.pkl","wb") as fp:
        pickle.dump(user_sim,fp)
    
    debug_user_sim(user_sim)
    recom_result = cal_recom_result(user_click,user_sim)
    debug_recom_result(recom_result,item_info)

if __name__=="__main__":
    main_flow()
