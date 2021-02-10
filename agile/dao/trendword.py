from agile.commons import dbutil
from agile.extensions import ma, db, cache
from agile.commons.pagination import paginate_bysql
from agile.consts import CATEGORY_MAP2ECDB


class BaseTrendWordDao:
    def __init__(self, category, mode, **kwargs):
        self.category = CATEGORY_MAP2ECDB.get(category, 'fab_clean')
        self.category_ag = category
        self.mode = mode


class ChinaECTrendWordDao(BaseTrendWordDao):
    top_benefit_sql = """
with cte as(
SELECT p2.zh_desc AS attribute,
			p1.date,
			dense_rank()over(partition by p2.id order by p1.date desc) as month_num,
            p1.popularity
           FROM attribute_trend p1
             JOIN attributes p2 ON p1.attribute_id = p2.id
             JOIN categories p3 ON p3.id = p2.category_id
          WHERE p1.dimension= '' -- 排除主流的功效
and p3.name=:cate and p2.level0='benefit' 
),cte_m3 as(
select
attribute,
avg(popularity) as popularity
from cte
where month_num<=3
group by attribute
), ctel as (
select attribute
from cte_m3 p1
where p1.popularity>=(select avg(popularity) from cte_m3)
order by popularity desc
)
select attribute from ctel
    """

    emerging_benefit_sql = """
    with cte as(
SELECT p2.zh_desc AS attribute,
			p1.date,
			dense_rank()over(partition by p2.id order by p1.date desc) as month_num,
            p1.impact_rank::int as impact,
            p1.popularity
           FROM attribute_trend p1
             JOIN attributes p2 ON p1.attribute_id = p2.id
             JOIN categories p3 ON p3.id = p2.category_id
          WHERE p1.dimension= '' and p3.name=:cate and p2.level0='benefit'
),
cte_m3 as(
select
    attribute,
    avg(impact) as impact,
    avg(popularity) as popularity
from cte
where month_num<=3
group by attribute
),
ctel as (
select
    p1.attribute, p1.impact
from cte_m3 p1
where p1.popularity<(select avg(popularity) from cte_m3)
)
select attribute
from ctel
order by impact desc
    """

    def get_benefit(self):
        sql = self.top_benefit_sql if self.mode == "top" else self.emerging_benefit_sql
        return paginate_bysql(sql, {'cate': self.category}, bind='ec', flat_list=True)

    exc_words = "配方,天然,不含,植物,自然植物,自然,技术,不伤手,因子,中性,亲肤,科技配方,鸡头,爱丽丝,花漾,工艺,两面针," + \
                "刺激,皮肤无刺激,科技,天然植物,花香,蛋白,不添加,护肤,草本植物,萃取天然植物精华,萃取植物," + \
                "天然成分,PH值,温和配方,分子,草本,植物配方,救必应,向前,益智,胎盘,天然原料,无害," + \
                "面膜,植萃,植物香型,水果,枝叶,活性物,草木,调理技术,表面活性剂," + \
                "花瓣,花果,花果香,鲜花,人发,酸性,第二步,科技,蔬菜,美容液,天然亲肤,果香,香精"

    top_ingredient_sql = f"""
WITH cte_stopwords AS (
         SELECT unnest.unnest AS word
           FROM unnest(string_to_array('{exc_words}', ',')) unnest(unnest)
        ),
cte as(
    select keyword as ingredient, goods_cnt from ec_ingre_freq p1
where category=:cate AND NOT (EXISTS ( SELECT s1.word
                   FROM cte_stopwords s1
                  WHERE s1.word = p1.keyword))
)
select ingredient
from cte
order by goods_cnt desc   
    """

    emerging_ingredient_sql = """
WITH cte as(
SELECT p1.ingredient,
			dense_rank()over(partition by p1.category order by p1.month desc) as month_num,
            p1.rank
           FROM public.ec_trend_rank p1
          WHERE p1.category=:cate and p1.ingredient_class ~* '^(ingre).*' and p1.ingredient_class !~* '.*mild.*'
)
select ingredient
from cte
where month_num=1
order by rank
    """

    def get_ingredient(self):
        sql = self.top_ingredient_sql if self.mode == "top" else self.emerging_ingredient_sql
        return paginate_bysql(sql, {'cate': self.category}, bind='ec', flat_list=True)


class ChinaSocailTrendWordDao(BaseTrendWordDao):
    top_benefit_sql = """
with cte as(
SELECT p2.zh_desc AS attribute,
			p1.date,
			dense_rank()over(partition by p2.id order by p1.date desc) as month_num,
            p1.msg_count as impact
           FROM wb_attr_trend p1
             JOIN attributes p2 ON p1.attribute = p2.name
			where p1.category=:cate and p2.level0='benefit' 
),
cte_m3 as(
select
attribute,
avg(impact) as impact
from cte
where month_num<=3
group by attribute
)
select attribute
from cte_m3
order by impact desc    
    """
    emerging_benefit_sql = """
with cte as(
SELECT p2.zh_desc AS attribute,
			p1.date,
			dense_rank()over(partition by p2.id order by p1.date desc) as month_num,
            p1.msg_count as impact
           FROM wb_attr_trend p1
             JOIN attributes p2 ON p1.attribute = p2.name
			where p1.category=:cate and p2.level0='benefit'
),
cte_m3 as(
select
attribute,
avg(impact) as impact
from cte
where month_num<=3
group by attribute
),
cte_m12 as(
select
attribute,
avg(impact) as impact
from cte
where month_num<=12
group by attribute
),
cte_grow as (
select
p1.attribute, p1.impact/p2.impact as growpct
from cte_m3 p1
inner join cte_m12 p2
on p1.attribute = p2.attribute
)
select attribute
from cte_grow
order by growpct desc
    """

    def get_benefit(self):
        sql = self.top_benefit_sql if self.mode == "top" else self.emerging_benefit_sql
        return paginate_bysql(sql, {'cate': self.category}, bind='ec', flat_list=True)

    top_ingredient_sql = """
WITH 
cte as(
    select keyword as ingredient,hotrank,
	dense_rank() over(partition by category order by quarter desc) as quarter_num
from weibo_ingredient_rank_abs_q p1
where category=:cate 
)
select ingredient
from cte
where quarter_num=1
order by hotrank
    """

    emerging_ingredient_sql = """
WITH 
cte as(
    select keyword as ingredient,hotrank,
	dense_rank() over(partition by category order by month desc) as month_num
from weibo_ingredient_rank_grow_50 p1
where category=:cate 
)
select ingredient
from cte
where month_num=1
order by hotrank
    """

    ic_top_ingredient_sql = """
    with ingre_mon as 
(
select attribute, month,buzz,dense_rank() over(order by month desc) as mon_num from weibo_statistics
where category_id=7 and datatype='flavor'
)
select 
	attribute as ingredient
from ingre_mon
where mon_num<=6
group by attribute
order by sum(buzz) desc
    """

    ic_emerge_ingredient_sql = """
with ingre_mon as 
(
select attribute, month,buzz,dense_rank() over(order by month desc) as mon_num from weibo_statistics
where category_id=7 and datatype='flavor'
)
,ingre_m3 as 
(
select 
	attribute,coalesce(sum(buzz),0) as buzz
from ingre_mon
where mon_num<=3
group by attribute
order by sum(buzz) desc
limit 200 offset 20
)
,ingre_m6 as 
(
select 
	attribute,coalesce(sum(buzz),0) as buzz
from ingre_mon
where mon_num between 4 and 6
group by attribute

)
select
	p1.attribute as ingredient
from ingre_m3 p1
left join ingre_m6 p2
on p1.attribute=p2.attribute
order by p1.buzz/(p2.buzz+1) desc
    """

    def get_ingredient(self):
        if self.category_ag == 'REI':
            sql = self.ic_top_ingredient_sql if self.mode == "top" else self.ic_emerge_ingredient_sql
            return paginate_bysql(sql, {'cate': self.category}, flat_list=True)
        else:
            sql = self.top_ingredient_sql if self.mode == "top" else self.emerging_ingredient_sql
            return paginate_bysql(sql, {'cate': self.category}, bind='ec', flat_list=True)


class OnePageTrendWordDao(BaseTrendWordDao):

    def get_benefit(self):
        sql = """
        with cte as(
        select p2.zh_desc as attribute from onepage_benefit_trend p1
inner join ec_attr p2
on p1.benefit=p2.level2 and p1.category=p2.category
where quarter=(select max(quarter) from onepage_benefit_trend)  and p1.category=:cate and mode=:mode
)  select * from cte
                """
        return paginate_bysql(sql, {'cate': self.category, 'mode': self.mode}, bind='ec', flat_list=True)

    def get_ingredient(self):
        sql = """
        with cte as(
        select ingredient from onepage_ingredient_trend p1
where quarter=(select max(quarter) from onepage_ingredient_trend) and p1.category=:cate and mode=:mode
) select * from cte
                """
        return paginate_bysql(sql, {'cate': self.category, 'mode': self.mode}, bind='ec', flat_list=True)
