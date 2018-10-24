import pickle
import operator
import math
import datetime


import sys
sys.path.append("../util")
import reader 
def update_contribute_score(user_click_times):
    return 1/math.log10(1+user_click_times)
def update_two_contribute_score(click_time1,click_time2):
    delata_time = abs(int(click_time1)-int(click_time2))
    total_sec = 60*60*24
    delata_time = delata_time/total_sec
    return 1/(1+delata_time)

def base_contribute_score():
    return 1

def cal_item_sim(user_click,user_click_time):
    """
    Args:
        user_click: dict，key:userid:value list[item1,item2...]
    return :
        dict:key itemid i,value dict:value_key itemid_j,value_value:simscore
    """
    co_appear={}
    item_user_click_times={}
    for user,itemlist in user_click.items():
        nu = len(itemlist)
        for index_i in range(0,len(itemlist)):
            itemid_i = itemlist[index_i]
            item_user_click_times.setdefault(itemid_i,0)
            item_user_click_times[itemid_i]+=1
            click_time1 = user_click_time[user+"_"+itemid_i]
            for index_j in range(index_i+1,len(itemlist)):                
                itemid_j = itemlist[index_j]
                click_time2 = user_click_time[user+"_"+itemid_j]
                co_appear.setdefault(itemid_i,{})
                co_appear.setdefault(itemid_j,{})
                co_appear[itemid_i].setdefault(itemid_j,0)
                co_appear[itemid_j].setdefault(itemid_i,0)
                # co_appear[itemid_i][itemid_j] += update_contribute_score(nu)
                # co_appear[itemid_j][itemid_i] += update_contribute_score(nu)
                co_appear[itemid_i][itemid_j] += update_two_contribute_score(click_time1,click_time2)
                co_appear[itemid_j][itemid_i] += update_two_contribute_score(click_time1,click_time2)
    item_sim_score = {}
    item_sim_score_sorted = {}
    for itemid_i,relate_item in co_appear.items():
        for itemid_j,co_time in relate_item.items():
            item_sim_score.setdefault(itemid_i,{})
            item_sim_score[itemid_i].setdefault(itemid_j,0)
            item_sim_score[itemid_i][itemid_j] = co_time/math.sqrt(item_user_click_times[itemid_j]*item_user_click_times[itemid_i])
    for itemid in item_sim_score:
        item_sim_score_sorted[itemid] = sorted(item_sim_score[itemid].items(),key=operator.itemgetter(1),reverse=True)
    return item_sim_score_sorted
def cal_recom_result(sim_info,user_click):
    """
    Recommond by itemcf
    Args:
        sim_info: item sim dict
        user_click: user click dict
    Returns:
        dict:key:userid value:dict value_key:itemid value_value:score 
    """
    recent_click_num = 3
    topK=5
    recom_info = {}
    recom_info_sorted = {}
    for user in user_click:
        click_list = user_click[user]
        recom_info.setdefault(user,{})
        for itemid in click_list[:recent_click_num]:
            for itemidsimzuhe in sim_info[itemid][:topK]:
                itemsimid = itemidsimzuhe[0]
                itemsimscore = itemidsimzuhe[1]
                recom_info[user].setdefault(itemsimid,0);
                recom_info[user][itemsimid] = itemsimscore
        recom_info_sorted[user] = sorted(recom_info[user].items(),key=operator.itemgetter(1),reverse=True)
    return recom_info_sorted

def debug_itemsim(item_info,sim_info):
    fixed_itemid = "1"
    [title,genres] = item_info[fixed_itemid]
    print("target :%s,genres:%s" % (title,genres))
    for zuhe in sim_info[fixed_itemid][:5]:
        itemid = zuhe[0]
        score  = zuhe[1]
        [itemtitle,itemgenres] = item_info[itemid]
        print(" score:%f name:%s genres:%s" %(score,itemtitle,itemgenres))

def debug_recommendresult(recom_result,item_info):
    user_id="1"
    for zuhe in recom_result[user_id]:
        itemid,score = zuhe
        print("movie: %s,genrens: %s,score:%f" %(item_info[itemid][0],item_info[itemid][1],score))

def main_flow():
    fn = "a.pkl"
    starttime = datetime.datetime.now()
    #long running
    user_click,user_click_time = reader.get_user_click("../ml-1m/ratings.dat")
    item_info = reader.get_item_info("../ml-1m/movies.dat")
    endtime = datetime.datetime.now()
    print("deal data: %d" % (endtime - starttime).seconds)

    '''
    with open(fn,"rb") as f:
        sim_info = pickle.load(f)
    '''
    starttime = datetime.datetime.now()
    sim_info = cal_item_sim(user_click,user_click_time)
    endtime = datetime.datetime.now()
    print("create sim_info: %d" % (endtime - starttime).seconds)
    
    with open(fn, 'wb') as f:                     
        picklestring = pickle.dump(sim_info, f)
    
    debug_itemsim(item_info,sim_info)
    starttime = datetime.datetime.now()
    #long running
    recom_result = cal_recom_result(sim_info,user_click)
    endtime = datetime.datetime.now()
    print("create recom_result: %d" % (endtime - starttime).seconds)  
    debug_recommendresult(recom_result,item_info)

if __name__=="__main__":
    main_flow()
