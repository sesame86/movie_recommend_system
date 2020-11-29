![main_page](/static/main_page.PNG)

# 영화 추천 시스템(collarborative filtering)
> 사이트

http://moviedelivery.shop/intro
- 가입하지 않고 보기
    - id : hello@naver.com
    - password : hello
> 기간
- 영화 추천 알고리즘 : 2020/03~2020/07
- 웹사이트 구현 : 2020/7~ 2020/8

> 프로젝트 간략 소개 한 문장 
- 사용자 기반 협업 필터링을 이용한 영화 추천 사이트

> 실행 환경
- pycharm
- mongodb
- HTML/CSS·Bootstrap·JQuery
- 가비아
- aws

> 사용한 데이터
- tmdb open api

웹페이지 구현에 이용

https://developers.themoviedb.org/3/getting-started/introduction

- MovieLens Latest Datasets

![use_data_sample](/static/use_data_sample.PNG)

-links로 합쳐서 tmdbid를 가져와서 사용

-mongodb에 저장후 비교할 사용자 데이터로 이용
    
https://grouplens.org/datasets/movielens/latest/

## 핵심 기능
- 사용자 기반 협업 필터링은 사용자가 평가한 영화 평점과 다른 사용자의 영화평점간의 유사도를 비교하여 유사도가 높은 사용자가 높게 평가한 영화를 사용자에게 추천해주는 알고리즘 입니다.

## 주요 코드
- knn 알고리즘
<pre><code>
    def nearest_neighbor_user(user, topN, simFunc):
        u1 = UM_matrix_ds.loc[user].dropna()
        ratedIndex = u1.index
        nn = {}

        ## 브루트 포스 알고리즘
        #조합 가능한 모든 문자열을 하나씩 대입해 보는 방식
        for uid, row in UM_matrix_ds.iterrows():
            interSectionU1 = []
            interSectionU2 = []
            if uid == user:
                continue
            for i in ratedIndex:
                if False == math.isnan(row[i]):
                    interSectionU1.append(u1[i])
                    interSectionU2.append(row[i])
            interSectionLen = len(interSectionU1)

            ## 최소 3개 교차한 아이템
            if interSectionLen < 3:
                continue

            ## 유사도 함수
            sim = simFunc(interSectionU1, interSectionU2)

            if math.isnan(sim) == False:
                nn[uid] = sim

        ## top 순위 대로 정렬
        return sorted(nn.items(), key=itemgetter(1), reverse=True)[:(topN + 1)]
</code></pre>
- 예상 점수 구하기
<pre><code>
    def predictRating(userid, nn=50, simFunc=distance_euclidean):

        ## knn함수
        neighbor = nearest_neighbor_user(userid, nn, simFunc)

        # 비슷한 유사도를 보이는 유저 리스트
        neighbor_id = [id for id, sim in neighbor]

        ## 4개이상이 NaN인 경우 제거
        neighbor_movie = UM_matrix_ds.loc[neighbor_id].dropna(1, how='all', thresh=4)

        neighbor_dic = (dict(neighbor))
        ret = []  # ['movieId', 'predictedRate']

        # 각 column을 순회한다. key : userid, column : movieid, value : rating
        for movieId, row in neighbor_movie.iteritems():
            jsum, wsum = 0, 0
            for v in row.dropna().iteritems():
                sim = neighbor_dic.get(v[0], 0)
                jsum += sim
                wsum += (v[1] * sim)
                rate = wsum / jsum
            ret.append([movieId, format(rate, '.2f')])

        return ret
</code></pre>
- 유클리디안 거리와 코사인 거리 측정 방법을 이용하여 두 벡터간의 유사도를 측정한 결과 유클리디언 거리를 이용한 모델의 MAE점수와 RMSE점수가 더 낮으므로 유클리디언 거리를 이용한 모델을 사용했습니다.

![use_data_sample](/static/평가.jpg)

## 결과물
![use_data_sample](/static/my_page1.PNG)
![use_data_sample](/static/my_page2.PNG)