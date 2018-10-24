import os
import codecs
def get_user_click(rating_file):
    """
    get user clcik list
    Args:
        rating_file:input_file
    Return:
        dict,key:userid,value:[item1,item2]
    """
    fp = open(rating_file)
    num=0
    user_click={}
    user_click_time = {}
    
    for line in fp:
        # num+=1
        # if(num>10000):
        #     break
        items = line.strip().split("::")
        uid = items[0]
        mid = items[1]
        rating = items[2]
        if float(rating)<3.0:
            continue
        if uid not in user_click:
            user_click[uid]=[]
        user_click[uid].append(mid)
        if items[0]+"_"+items[1] not in user_click_time:
            user_click_time[items[0]+"_"+items[1]] = items[3]
    fp.close()
    return user_click,user_click_time

def get_item_info(item_file):
    """
    get item info[title,genres]
    Args:
        item_file:input iteminfo file
    Return:
        a dict,key itemid,value:[title,genres]
    
    """
    fp = codecs.open(item_file,'r',encoding = "ISO-8859-1")
    item_info = {}
    for line in fp:
        items = line.strip().split("::")
        if items[0] not in item_info:
            item_info[items[0]]=[items[1],items[2]]
    fp.close()
    return item_info
if __name__=="__main__":
    user_click,user_click_time =get_user_click("/Users/wangsen/al/cf/ml-1m/ratings.dat")
    print(len(user_click))
    print(user_click["1"])
    item_info = get_item_info("/Users/wangsen/al/cf/ml-1m/movies.dat")
    print(len(item_info))
    print(item_info["1"])
    print(len(user_click_time))

