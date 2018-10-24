> 推荐算法是对我们现实生活影响最大的计算机算法，它影响了我们看到的新闻、广告、以及我们身边现实环境的东西，这些最终决定了我们的态度和生活方式，尤瓦尔.赫拉利在《未来简史》中声明“算法会比我们更了解自己”。
>
> 本文介绍了一种较基础的推荐算法，协同过滤Collaborative Filtering。基于用户购买的历史商品推荐，物品协同过滤；基于用户相似用户购买物品的推荐，用户协同过滤。
>
> 随着用户信息越来越多被采集，推荐系统可以勾画出一个人的用户画像，现在更多系统用户画像结合现场信息实现推荐系统。下一步我会实现一个基于用户画像的推荐系统。
> 本文根据课程整理： https://www.imooc.com/learn/1029。
>作者github代码：https://github.com/birdskyws/CollaborativeFiltering
## 推荐算法
#### 一、推荐系统作用
帮助用户发现他们想要的物品，另一方面将物品曝光在对自己感兴趣的用户群体面前。

#### 二、如何评价一个好的推荐系统
##### 业务指标
- 信息流
    - 点击率：点击次数/展示次数。一定展示次数，点击越多越好。
    - 平均阅读时长:（1）总阅读时长/人平均点击次数。平均阅读时长越大，推荐越准。（2）使用总时长/展示个数。使用总时越长越好。
- 电商
    - 转化率（1）总成交次数/展示次数（2）单位时间成交额。
##### 推荐覆盖率
推荐覆盖率 = 去重推荐物品/总物品  
推荐覆盖率越高越好。
##### offline vs online
- offine。通过模型和数据，模拟用户记录，进行数据统计。
- online。ABTest，当Offine的算法指标不低于基线，可以用一部分信息流作为测试，运行一段时间后，将统计这段信息流和整体指标的差异，判断新算法的好坏。
#### 三、工业界落地场景
1. 信息流。今日头条、百度feed、UC头条
2. 电商。猜你喜欢
3. o2o，LBS。基于地理位置信息的推荐系统。
#### 架构设计
![](https://upload-images.jianshu.io/upload_images/6234504-a6d7ab5436e85cb1.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
- App 用户端
- Web Api，接收App用户访问信息，调用后端RPC功能，WebApi尽量不做业务逻辑，但是完成消息队列、日志记录等工作。消息队列：削峰填谷。日志记录：大数据分析、模型训练。
- Match：个性化召回。基于物品或用户推荐规则，计算应该给用户提供的商品。
- Rank。推荐物品排序，模型打分,决定物品展示顺序。
- Strategy。推荐系统基于业务场景的规则，由于召回算法Match和排序算法Rank都是基于模型的，因此可以定制一些场景调整模型结果。
#### 四、工业界系统架构
![](https://upload-images.jianshu.io/upload_images/6234504-fa6de5d78c6fe4af.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
- model&KV：离线模型。根据用户行为计算推荐结果，主要功能（1)计算item之间的相似度(2)计算行为相近的用户（3）计算某种Label item的排序，例如用户喜欢体育，计算所有体育类item的排序。这些结果写入KV存储。
- RecallServer&KV:召回服务器从KV服务器中读取结果。Recall，召回，从item集合中选出推荐服务，即为召回。KV，key-value存储(RDBMS,关系型数据库）。KV更适合做缓存，访问速度快。
- DocDetailServer:从KV存储获取itemID后，通过Doc Detail Server查询item的详细信息，通过模板拼接后发送给用户。
- 深度学习模型：将用户特性向量化UserEmbeding，itemEmbeding存储在KV中，实现K近邻搜索算法。
## Item cf 基于物品协同过滤
#### 1. 原理
![](https://upload-images.jianshu.io/upload_images/6234504-53e48f8c4777c760.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
此系统中存在：
- 用户 A B C D
- 商品 a b c d  
用户A购买过a、b、d；用户B购买过b、c、e。 
建立物品对用户的索引(**倒排索引**)：a商品对应物品AD;b商品对应ADC 。在结果中比较，会到物品a和d购买的用户重合度较大，那么a和d就可以做近似推荐。即可以给用户C推荐物品a。
#### 2. 公式
![Item CF公式](https://upload-images.jianshu.io/upload_images/6234504-2a1a7ff462654432.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
- Sij，代表物品i和物品j的相识度。分子：“行为过”物品i和物品j的用户的交集；分母：“行为过”物品i和物品j的用户的并集。
- Puj，计算用户U对物品j的评分，即用户U没有行为过物品j，我们要预测这个值。根据Sij（协同矩阵）进行打分。
    - (1)选出用户U的行为物品N(u),在N(u)中选出和物品j（目标物品）评分接近k个物品，（Sij矩阵中评分越大越接近）   
    - (2)这些物品的用户U评分(Rui)的加权和，就是用户U对物品j的推荐评分。
![惩罚热门商品](https://upload-images.jianshu.io/upload_images/6234504-d33ef4d882223998.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

公式升级1中缩小分子，非活跃用户惩罚程度小，活跃用户惩罚程度大。
![时间惩罚](https://upload-images.jianshu.io/upload_images/6234504-7000c6effe665e9b.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)  

原公式中，只考虑用户消费用一种商品，而没有考虑用户消费同一种商品处在不同时期。如果用户消费了物品i和物品j，如果消费时间间隔越近，那么这次“同现”的权重应该越大，间隔越远权重越小。在分子上除以间隔时间，惩罚时间间隔影响。
## User CF 基于用户协同过滤推荐算法
#### 原理
![user cf](https://upload-images.jianshu.io/upload_images/6234504-fd315b6658d34c0b.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
此系统中存在：
- 用户 A B C D
- 商品 a b c d  

用户A消费过a，d，b三件商品，用户D消费过a，d两件物品。通过计算，用户A和用户D消费过的物品相识度较高，那么认为用户A和用户D兴趣相识，可以将用户A购买过的商品推荐给用户D。上面的例子可以将物品b推荐给用户D。
#### 公式
![user cf](https://upload-images.jianshu.io/upload_images/6234504-544ba9e79948dc4c.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
- Suv，用户u和用户v的相识度。分子为用户u和用户v的行为过的物品交集，分母为用户u和用户v的行为过物品的并集。用户u、用户v同时用过的物品越多，Suv越大，用户相识度越大。
- Pui 用户u对商品i的预测评分
    - (1)选出行为过物品i的用户集合U(i)，选择U(i)中和u用户（目标用户）相近的k个用户（Suv越大越相近）.
    - (2)计算加权评分（Rvi）。

![惩罚热门商品](https://upload-images.jianshu.io/upload_images/6234504-7b4f9ba1eb887da1.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
如果用户u和用户v，购买过同样的热门商品较多，不能说明两个用户之间的兴趣行为相识。  

在usercf公式升级1中，分子中每一项物品除以销售数，那么每一件物品的贡献率范围为1~0，物品销售越多越趋近于0，贡献越小。这样惩罚了热门商品对计算用户协同矩阵的影响。
![惩罚购买间隔](https://upload-images.jianshu.io/upload_images/6234504-e6d7daa79bfb875f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
如果用户u和用户v，购买过同样的商品的时间间隔越长，那么也应该降低该商品对用户协同矩阵的影响。
## ItemCF 与 UserCF的比较
#### 推荐实时性  
UserCF实时性差。基于用户相似性矩阵，用户在使用系统过程中，短期少量行为，不会改变与其他用户的相识度（行为没有太多改变，参考Suv），那么就不会推荐新物品。   
ItemCF实时性高。当用户行为了一个新的物品，这个新物品的相关物品，根据推荐算法会获得高Rank，很快被推荐。  
#### 新物品、新用户推荐
UserCf，不能给新用户推荐，新用户没有行为，不能构建用户协同矩阵，无法根据相似用户给新用户推荐；新物品被一个用户行为，和这个用户相似用户会得到这个新物品推荐。  
ItemCf，不能推荐新物品，该物品没有加入协同矩阵。可以给新用户推荐行为物品的相识物品。  
#### 推荐系统的可解释性
UserCf，基于相似用户推荐，很难说明相识用户的喜好 。  
ItemCF，基于用户点击过的物品进行推荐，解释性好。  
#### ItemCf和UserCf 应用场景
- 性能：构建相似矩阵计算代价比较高，真实环境下的系统用户数远大于商品数，从性能考虑采用ItemCF。
- 个性化：UserCf适用于要求物品及时下发，且个性化要求不强烈的场景。ItemCF适合物品丰富，且个性化强烈的场景。  
应用ItemCF的应用场景可以结合其他召回策略及时下发新产品，所以更倾向于ItemCF.
