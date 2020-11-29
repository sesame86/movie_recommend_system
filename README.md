<img src="https://postfiles.pstatic.net/MjAyMDA4MjVfMjY3/MDAxNTk4MzMzMTMzMzYz.TecBsMZiaVib0wlGrjzDyqGKUVHQFuK7ByVss1u_pEQg.5OjcSo9t3u5bxnj8zyp5qfDm102rGaX7Wp1uB-_Pm2sg.JPEG.kyy8006/logo.jpg?type=w773" height="100"/>

# 영화 추천 시스템(collarborative filtering)
실행 환경
- pycharm
- mongodb

이용 도메인
- 가비아


사용한 데이터
- tmdb open api :  웹페이지 구현에 이용
https://developers.themoviedb.org/3/getting-started/introduction
- MovieLens Latest Datasets : links로 합쳐서 tmdbid를 가져와서 사용, 비교할 사용자 데이터로 이용
https://grouplens.org/datasets/movielens/latest/

> 프로젝트 간략 소개 한 문장 
- 사용자 기반 협업 필터링을 이용한 영화 추천 사이트


## 핵심 기능  Key Feature
- 사용자 기반 협업 필터링은 사용자가 평가한 영화 평점과 다른 사용자의 영화평점간의 유사도를 비교하여 유사도가 높은 사용자가 높게 평가한 영화를 사용자에게 추천해주는 알고리즘 입니다.
- 유클리디안 거리와 코사인 거리 측정 방법을 이용하여 두 벡터간의 유사도를 측정했습니다.

> 사이트
http://moviedelivery.shop/intro