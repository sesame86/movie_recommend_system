![main_page](/static/main_page.PNG)

# 영화 추천 시스템(collarborative filtering)
> 사이트

http://moviedelivery.shop/intro
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
    - 웹페이지 구현에 이용
    
https://developers.themoviedb.org/3/getting-started/introduction

- MovieLens Latest Datasets

![use_data_sample](/static/use_data_sample.PNG)
    - links로 합쳐서 tmdbid를 가져와서 사용
    - mongodb에 저장후 비교할 사용자 데이터로 이용
    
https://grouplens.org/datasets/movielens/latest/

## 핵심 기능
- 사용자 기반 협업 필터링은 사용자가 평가한 영화 평점과 다른 사용자의 영화평점간의 유사도를 비교하여 유사도가 높은 사용자가 높게 평가한 영화를 사용자에게 추천해주는 알고리즘 입니다.
- 유클리디안 거리와 코사인 거리 측정 방법을 이용하여 두 벡터간의 유사도를 측정한 결과 유클리디언 거리를 이용한 모델의 MAE점수와 RMSE점수가 더 낮으므로 유클리디언 거리를 이용한 모델을 사용했습니다.

![use_data_sample](/static/평가.jpg)

