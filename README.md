# 反爬虫系列
- **cnki**：知网论文系统爬虫
    - 从[http://www.cnki.net/](http://www.cnki.net/)搜索入口，本爬虫是搜索文献来源的，可限定年限，搜索其它类别的原理一样。访问搜索url后，每次访问其它url时就要带上搜索的cookies，不然出来的数据不对。
- **datamodel**：易车指数的对比和关注指数爬虫
    - 从[http://datamodel.bitauto.com/](http://datamodel.bitauto.com/)搜索入口，输入车型名称，查询各种指数。类似知网访问后面的url也要一直带上搜索的cookies，此外访问搜索url时还要带上headers，其中的referer必须有。
- **sougou**：搜狗搜索微信爬虫