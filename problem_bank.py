from dataclasses import dataclass
from typing import List


@dataclass
class Problem:
    pid: str
    title: str
    body: str
    difficulty: str
    kind: str  # "sql" or "pyspark"
    expected: List[str]
    hint: str


DIFFICULTY_OPTIONS = [
    "Lv1 입문",
    "Lv2 초급",
    "Lv3 중급",
    "Lv4 고급",
    "Lv5 심화",
]


PROBLEM_BANK: List[Problem] = [
    Problem(
        pid="sql_select_filter",
        title="신규 고객 목록 조회",
        body=(
            "customers 테이블에서 가입일이 2024-01-01 이후인 고객의 id, name, signup_date를 "
            "최근 가입일 순으로 조회하세요."
        ),
        difficulty="Lv1 입문",
        kind="sql",
        expected=["SELECT", "WHERE", "ORDER BY"],
        hint="기본 SELECT와 WHERE 조건, ORDER BY로 정렬합니다.",
    ),
    Problem(
        pid="sql_aggregation_monthly",
        title="월별 매출 합계 구하기",
        body=(
            "sales 테이블에서 월별 총 매출액을 계산하세요. 컬럼은 month, total_sales 로 하고 "
            "결과는 월 오름차순으로 정렬하세요."
        ),
        difficulty="Lv2 초급",
        kind="sql",
        expected=["GROUP BY", "SUM", "ORDER BY"],
        hint="GROUP BY와 DATE_TRUNC 또는 MONTH 함수를 활용해 월 단위로 묶으세요.",
    ),
    Problem(
        pid="sql_join_customer_orders",
        title="고객별 주문 금액 합계",
        body=(
            "customers(cust_id, name)와 orders(order_id, cust_id, amount) 테이블을 조인해 "
            "고객 이름과 총 주문 금액을 조회하세요. 금액이 높은 순으로 정렬하세요."
        ),
        difficulty="Lv3 중급",
        kind="sql",
        expected=["JOIN", "GROUP BY", "SUM", "ORDER BY"],
        hint="INNER JOIN으로 연결한 뒤 cust_id를 기준으로 SUM(amount)를 집계합니다.",
    ),
    Problem(
        pid="sql_group_having",
        title="평균 단가 상위 카테고리",
        body=(
            "products(category, price)에서 카테고리별 평균 단가가 50000 이상인 카테고리를 찾고 "
            "평균 단가 내림차순으로 정렬하세요."
        ),
        difficulty="Lv3 중급",
        kind="sql",
        expected=["GROUP BY", "AVG", "HAVING", "ORDER BY"],
        hint="GROUP BY로 묶은 뒤 HAVING으로 평균 조건을 거세요.",
    ),
    Problem(
        pid="sql_window_rank",
        title="카테고리별 최고 판매 상품 찾기",
        body=(
            "products(id, category, price) 테이블에서 카테고리별로 가장 비싼 상품의 id와 price를 구하세요."
        ),
        difficulty="Lv4 고급",
        kind="sql",
        expected=["ROW_NUMBER", "PARTITION BY", "ORDER BY"],
        hint="ROW_NUMBER() OVER(PARTITION BY category ORDER BY price DESC)로 1순위만 남기세요.",
    ),
    Problem(
        pid="sql_running_total",
        title="월별 누적 매출 계산",
        body=(
            "sales(month, amount)에서 월별 매출과 누적 매출 cum_sales를 구하세요. 월 기준 오름차순으로 출력하세요."
        ),
        difficulty="Lv5 심화",
        kind="sql",
        expected=["SUM", "OVER", "ORDER BY", "PARTITION"],
        hint="CTE로 월별 집계를 만든 뒤 SUM(amount) OVER(ORDER BY month)로 누적합을 계산합니다.",
    ),
    Problem(
        pid="pyspark_basic_filter",
        title="활성 사용자 필터링",
        body=(
            "users DataFrame에서 active가 True이고 last_login이 2024-01-01 이후인 사용자만 남기고 "
            "id와 last_login 컬럼을 선택하세요."
        ),
        difficulty="Lv1 입문",
        kind="pyspark",
        expected=["filter", "select"],
        hint="filter로 조건을 연결하고 select로 필요한 컬럼만 남깁니다.",
    ),
    Problem(
        pid="pyspark_join",
        title="고객 주문 통계 만들기",
        body=(
            "customers와 orders DataFrame이 주어졌을 때, 고객별 주문 건수와 총 금액을 계산하는 DataFrame을 만들고 "
            "order_count, total_amount 컬럼을 추가하세요."
        ),
        difficulty="Lv2 초급",
        kind="pyspark",
        expected=["join", "groupBy", "agg"],
        hint="join 후 groupBy로 집계하고 count, sum 집계함수를 사용하세요.",
    ),
    Problem(
        pid="pyspark_window",
        title="이동 평균 계산",
        body=(
            "time, value 컬럼을 가진 DataFrame에서 최근 3개 행의 이동 평균 rolling_avg 컬럼을 추가하세요."
        ),
        difficulty="Lv3 중급",
        kind="pyspark",
        expected=["Window", "rowsBetween", "avg"],
        hint="Window.orderBy('time').rowsBetween(-2, 0) 범위로 avg를 계산하세요.",
    ),
    Problem(
        pid="pyspark_pivot",
        title="주간 상태별 집계 피벗",
        body=(
            "logs DataFrame(timestamp, status)에 대해 주차별(status별) 건수를 피벗 형태로 계산하세요. "
            "week, success, fail 같은 컬럼이 나오도록 만드세요."
        ),
        difficulty="Lv4 고급",
        kind="pyspark",
        expected=["groupBy", "pivot", "count", "date_trunc"],
        hint="week 컬럼을 date_trunc('week', timestamp)로 만든 뒤 pivot(status) 후 count 합니다.",
    ),
    Problem(
        pid="pyspark_sessionize",
        title="세션 분리하여 페이지뷰 집계",
        body=(
            "pageviews(user_id, ts)에서 사용자별 30분 이상 끊기면 새로운 세션이라고 가정할 때, "
            "세션 번호 session_id를 붙이고 세션당 페이지뷰 수를 집계하세요."
        ),
        difficulty="Lv5 심화",
        kind="pyspark",
        expected=["Window", "lag", "when", "sum", "over"],
        hint="user_id 파티션에서 lag(ts)로 이전 시각과 차이를 구하고, when으로 세션 리셋 플래그를 만든 뒤 sum를 over 으로 누적합합니다.",
    ),
    Problem(
        pid="sql_001_daily_unique_users",
        title="일별 고유 사용자 수 집계",
        body="activity(user_id, ts)에서 일별(unique user 수)을 계산하세요.",
        difficulty="Lv1 입문",
        kind="sql",
        expected=["COUNT(DISTINCT ...)", "GROUP BY", "DATE_TRUNC"],
        hint="DATE_TRUNC('day', ts)로 묶어 distinct count."
    ),
    Problem(
        pid="sql_002_top3_products_by_category",
        title="카테고리별 판매 상위 3개 상품",
        body="sales(product_id, category, amount)에서 카테고리별 판매 상위 3개 상품을 찾으세요.",
        difficulty="Lv2 초급",
        kind="sql",
        expected=["ROW_NUMBER", "PARTITION BY", "SUM"],
        hint="ROW_NUMBER()로 상위 3개만."
    ),
    Problem(
        pid="sql_003_first_login_flag",
        title="신규/복귀 사용자 구분",
        body="logins(user_id, date)에서 첫 로그인일을 기준으로 2024년 신규 여부를 표시하세요.",
        difficulty="Lv3 중급",
        kind="sql",
        expected=["MIN", "GROUP BY", "CASE WHEN"],
        hint="MIN(login_date)로 신규 여부 판별."
    ),
    Problem(
        pid="sql_004_recent3_order_avg",
        title="최근 3건 주문 평균",
        body="orders(cust_id, order_date, amount)에서 cust_id별 최근 3건 평균 amount.",
        difficulty="Lv4 고급",
        kind="sql",
        expected=["ROW_NUMBER", "PARTITION", "AVG"],
        hint="order_date desc로 3건만."
    ),
    Problem(
        pid="sql_005_customer_last_order",
        title="고객별 마지막 주문일",
        body="orders(cust_id, date)에서 고객별 최신 주문일을 조회하세요.",
        difficulty="Lv1 입문",
        kind="sql",
        expected=["MAX", "GROUP BY"],
        hint="MAX(date) 사용."
    ),
    Problem(
        pid="sql_006_monthly_active_users",
        title="월간 활성 사용자 수",
        body="events(user_id, ts)에서 월별 unique user 수를 계산하세요.",
        difficulty="Lv2 초급",
        kind="sql",
        expected=["COUNT(DISTINCT ...)", "GROUP BY", "DATE_TRUNC"],
        hint="DATE_TRUNC('month')."
    ),
    Problem(
        pid="sql_007_product_price_rank",
        title="카테고리별 가격 순위",
        body="products(id, category, price)에서 카테고리별 price rank를 계산하세요.",
        difficulty="Lv3 중급",
        kind="sql",
        expected=["RANK", "PARTITION BY"],
        hint="OVER(PARTITION BY category ORDER BY price DESC)."
    ),
    Problem(
        pid="sql_008_avg_daily_sales",
        title="일평균 매출",
        body="sales(date, amount)에서 전체 기간 일평균 매출을 계산하세요.",
        difficulty="Lv1 입문",
        kind="sql",
        expected=["AVG"],
        hint="단순 AVG(amount)."
    ),
    Problem(
        pid="sql_009_customer_revenue_segment",
        title="고객 매출 구간 분류",
        body="orders(cust_id, amount) 총액 기준으로 고객을 등급(S/M/L)으로 분류하세요.",
        difficulty="Lv3 중급",
        kind="sql",
        expected=["SUM", "CASE WHEN", "GROUP BY"],
        hint="SUM(amount)로 등급 나누기."
    ),
    Problem(
        pid="sql_010_hourly_event_count",
        title="시간대별 이벤트 건수",
        body="events(id, ts)에서 시간별 event count.",
        difficulty="Lv1 입문",
        kind="sql",
        expected=["DATE_TRUNC('hour')", "GROUP BY"],
        hint="hour 단위 DATE_TRUNC."
    ),
    Problem(
        pid="sql_011_abnormal_high_value",
        title="고액 이상치 탐지",
        body="transactions(amount)에서 평균 대비 3배 초과 거래를 찾으세요.",
        difficulty="Lv3 중급",
        kind="sql",
        expected=["AVG", "HAVING"],
        hint="HAVING amount > 3 * avg_amount."
    ),
    Problem(
        pid="sql_012_first_purchase_after_signup",
        title="가입 후 첫 구매일 조회",
        body="users(u_id, signup)와 orders(u_id, order_date)에서 첫 order_date를 찾으세요.",
        difficulty="Lv3 중급",
        kind="sql",
        expected=["JOIN", "MIN", "GROUP BY"],
        hint="MIN(order_date)."
    ),
    Problem(
        pid="sql_013_repeat_rate",
        title="재구매율 계산",
        body="orders(customer_id)에서 2회 이상 구매한 고객 비율을 구하세요.",
        difficulty="Lv4 고급",
        kind="sql",
        expected=["COUNT", "GROUP BY", "HAVING"],
        hint="HAVING count(*)>=2."
    ),
    Problem(
        pid="sql_014_conversion_funnel",
        title="단계별 전환율 집계",
        body="funnel(user_id, step)에서 step1→step2→step3 전환율 계산.",
        difficulty="Lv5 심화",
        kind="sql",
        expected=["COUNT DISTINCT", "CASE", "SUBQUERY"],
        hint="각 step별 unique user count."
    ),
    Problem(
        pid="sql_015_daily_retention",
        title="일간 다음날 유지율 계산",
        body="logins(user_id, date)에서 D-day와 D+1 모두 로그인한 사용자 비율.",
        difficulty="Lv5 심화",
        kind="sql",
        expected=["SELF JOIN"],
        hint="date = d, date = d+1로 self join."
    ),
    Problem(
        pid="sql_016_user_gap_days",
        title="로그인 간격 계산",
        body="logins(user_id, ts)에서 사용자별 이전 로그인과의 일수 차를 계산하세요.",
        difficulty="Lv4 고급",
        kind="sql",
        expected=["LAG", "DATE_DIFF"],
        hint="LAG(ts) OVER(PARTITION...)."
    ),
    Problem(
        pid="sql_017_customer_latest_status",
        title="고객 최신 상태 조회",
        body="status_logs(customer_id, ts, status)에서 가장 최근 상태 1건.",
        difficulty="Lv3 중급",
        kind="sql",
        expected=["ROW_NUMBER", "ORDER BY DESC"],
        hint="rn=1만."
    ),
    Problem(
        pid="sql_018_product_sales_growth",
        title="제품 월별 매출 증감률",
        body="sales(product_id, month, amount)에서 이전 달 대비 증가율 계산.",
        difficulty="Lv4 고급",
        kind="sql",
        expected=["LAG", "OVER"],
        hint="(curr - prev)/prev."
    ),
    Problem(
        pid="sql_019_cross_sell_candidates",
        title="교차 판매 후보 상품",
        body="basket(order_id, product)에서 함께 구매된 product pair 조회.",
        difficulty="Lv5 심화",
        kind="sql",
        expected=["SELF JOIN"],
        hint="같은 order_id끼리 join."
    ),
    Problem(
        pid="sql_020_category_penetration",
        title="카테고리 도달률 계산",
        body="user_category(user_id, category)에서 전체 대비 category 비율.",
        difficulty="Lv2 초급",
        kind="sql",
        expected=["COUNT", "GROUP BY"],
        hint="전체 user 수 대비."
    ),
    Problem(
        pid="sql_021_user_longest_streak",
        title="최장 연속 로그인 기간",
        body="logins(user_id, date)에서 연속 출석 streak 계산.",
        difficulty="Lv5 심화",
        kind="sql",
        expected=["LAG", "CASE WHEN", "SUM OVER"],
        hint="끊김 flag 누적."
    ),
    Problem(
        pid="sql_022_order_gap_avg",
        title="평균 주문 간격",
        body="orders(cust_id, order_date)에서 고객별 평균 날짜 간격.",
        difficulty="Lv3 중급",
        kind="sql",
        expected=["LAG", "DATE_DIFF"],
        hint="LAG 후 avg."
    ),
    Problem(
        pid="sql_023_top_country_sales",
        title="국가별 매출 Top5",
        body="sales(country, amount)에서 top5 국가.",
        difficulty="Lv1 입문",
        kind="sql",
        expected=["SUM", "ORDER BY", "LIMIT"],
        hint="sum(amount) desc limit 5."
    ),
    Problem(
        pid="sql_024_first_touch_attribution",
        title="첫 접점 기여도",
        body="touches(user_id, ts, channel)에서 첫 접점 채널별 사용자 수.",
        difficulty="Lv4 고급",
        kind="sql",
        expected=["ROW_NUMBER", "PARTITION BY"],
        hint="rn=1."
    ),
    Problem(
        pid="sql_025_revenue_percentile",
        title="매출 상위 10% 고객 찾기",
        body="orders(cust_id, amount) 총액 기준으로 상위 10% 고객.",
        difficulty="Lv5 심화",
        kind="sql",
        expected=["PERCENT_RANK"],
        hint="percent_rank over."
    ),
    Problem(
        pid="sql_026_user_cohort",
        title="월 Cohort 분석",
        body="signup month 기준으로 cohort별 N달차 잔존율 계산.",
        difficulty="Lv5 심화",
        kind="sql",
        expected=["DATE_TRUNC", "JOIN", "COUNT DISTINCT"],
        hint="cohort vs activity."
    ),
    Problem(
        pid="sql_027_order_share",
        title="카테고리별 매출 비중",
        body="sales(category, amount) 전체 대비 카테고리 비중.",
        difficulty="Lv2 초급",
        kind="sql",
        expected=["SUM", "WINDOW"],
        hint="sum(amount)/sum(amount) over()."
    ),
    Problem(
        pid="sql_028_hourly_anomaly",
        title="시간대 이상 탐지",
        body="hourly_stats(hour, cnt)에서 평균 대비 2표준편차 초과 시간대.",
        difficulty="Lv4 고급",
        kind="sql",
        expected=["AVG", "STDDEV", "HAVING"],
        hint="cnt > avg + 2*stddev."
    ),
    Problem(
        pid="sql_029_user_latest_action",
        title="최근 행동 1건",
        body="events(user_id, ts, action)에서 가장 최근 action.",
        difficulty="Lv2 초급",
        kind="sql",
        expected=["ROW_NUMBER"],
        hint="order by ts desc limit 1 per user."
    ),
    Problem(
        pid="sql_030_multi_category_users",
        title="다카테고리 이용 사용자",
        body="user_cat(user_id, category)에서 category 3개 이상 이용한 유저.",
        difficulty="Lv3 중급",
        kind="sql",
        expected=["COUNT DISTINCT", "HAVING"],
        hint="having count(distinct category)>=3."
    ),
    Problem(
        pid="sql_031_daily_new_users",
        title="일간 신규 사용자 수",
        body="users(user_id, signup_date) 일별 신규 count.",
        difficulty="Lv1 입문",
        kind="sql",
        expected=["GROUP BY"],
        hint="date(signup_date)."
    ),
    Problem(
        pid="sql_032_revenue_running_total_by_cat",
        title="카테고리별 누적 매출",
        body="sales(category, month, amount)에서 카테고리별 누적 합.",
        difficulty="Lv4 고급",
        kind="sql",
        expected=["SUM OVER", "PARTITION"],
        hint="sum(amount) over(partition...)."
    ),
    Problem(
        pid="sql_033_session_length",
        title="로그 세션 길이 계산",
        body="sessions(user_id, start_ts, end_ts)에서 session duration.",
        difficulty="Lv1 입문",
        kind="sql",
        expected=["DATE_DIFF"],
        hint="end-start."
    ),
    Problem(
        pid="sql_034_refund_rate",
        title="환불 비율",
        body="orders(status)에서 refund 비율.",
        difficulty="Lv1 입문",
        kind="sql",
        expected=["COUNT", "CASE"],
        hint="refund count / total."
    ),
    Problem(
        pid="sql_035_top_city_by_users",
        title="도시별 사용자 수 rank",
        body="users(city, user_id) 도시별 user count ranking.",
        difficulty="Lv2 초급",
        kind="sql",
        expected=["COUNT", "RANK"],
        hint="rank over order by count desc."
    ),
    Problem(
        pid="sql_036_repeat_purchase_interval",
        title="재구매 간격 평균",
        body="orders(user_id, ts)에서 user별 LAG 이용.",
        difficulty="Lv4 고급",
        kind="sql",
        expected=["LAG", "AVG"],
        hint="lag(ts)."
    ),
    Problem(
        pid="sql_037_cart_conversion",
        title="장바구니 → 구매 전환율",
        body="cart(user_id) vs orders(user_id) join.",
        difficulty="Lv3 중급",
        kind="sql",
        expected=["LEFT JOIN"],
        hint="cart 기준 join."
    ),
    Problem(
        pid="sql_038_top5_tags",
        title="가장 많이 쓰인 태그 Top5",
        body="tags(post_id, tag) count.",
        difficulty="Lv1 입문",
        kind="sql",
        expected=["COUNT", "ORDER BY"],
        hint="desc limit 5."
    ),
    Problem(
        pid="sql_039_month_over_month_growth",
        title="월별 MoM 성장률",
        body="monthly(amount)에서 lag(amount).",
        difficulty="Lv4 고급",
        kind="sql",
        expected=["LAG", "OVER"],
        hint="(curr-prev)/prev."
    ),
    Problem(
        pid="sql_040_user_engagement_score",
        title="사용자 참여 점수 계산",
        body="log(type)에서 event별 가중치 합.",
        difficulty="Lv3 중급",
        kind="sql",
        expected=["SUM", "CASE"],
        hint="CASE로 가중치."
    ),
    Problem(
        pid="sql_041_max_gap_user",
        title="최대 활동 공백 유저",
        body="events(user_id, ts)에서 gap 가장 큰 user.",
        difficulty="Lv5 심화",
        kind="sql",
        expected=["LAG", "MAX"],
        hint="ts - lag(ts)."
    ),
    Problem(
        pid="sql_042_top_search_terms",
        title="검색어 Top10",
        body="search(term) 집계.",
        difficulty="Lv1 입문",
        kind="sql",
        expected=["COUNT"],
        hint="order desc limit 10."
    ),
    Problem(
        pid="sql_043_zero_sales_days",
        title="판매 0건 날짜 조회",
        body="calendar join sales.",
        difficulty="Lv3 중급",
        kind="sql",
        expected=["LEFT JOIN"],
        hint="null count."
    ),
    Problem(
        pid="sql_044_user_first_vs_last_diff",
        title="첫/마지막 로그인 차이",
        body="logins(user_id, ts).",
        difficulty="Lv2 초급",
        kind="sql",
        expected=["MIN", "MAX"],
        hint="max-min."
    ),
    Problem(
        pid="sql_045_multi_buy_pairs",
        title="같이 구매된 상품 쌍 집계",
        body="basket(order_id, product).",
        difficulty="Lv5 심화",
        kind="sql",
        expected=["SELF JOIN"],
        hint="same order."
    ),
    Problem(
        pid="sql_046_top_country_growth",
        title="국가별 성장률",
        body="sales(country, month, amount).",
        difficulty="Lv4 고급",
        kind="sql",
        expected=["LAG"],
        hint="lag(month)."
    ),
    Problem(
        pid="sql_047_inactive_users",
        title="30일 이상 미접속 유저",
        body="logins(user_id, last_login).",
        difficulty="Lv2 초급",
        kind="sql",
        expected=["DATE_DIFF"],
        hint="now-last_login."
    ),
    Problem(
        pid="sql_048_purchase_freq_distribution",
        title="구매 빈도 분포",
        body="orders(user_id).",
        difficulty="Lv2 초급",
        kind="sql",
        expected=["COUNT", "GROUP BY"],
        hint="user당 count."
    ),
    Problem(
        pid="sql_049_customer_lifetime_value",
        title="고객 LTV 추정",
        body="orders(cust_id, amount) 평균×빈도.",
        difficulty="Lv5 심화",
        kind="sql",
        expected=["SUM", "AVG", "JOIN"],
        hint="amount sum / months."
    ),
    Problem(
        pid="sql_050_weekly_retention",
        title="주간 잔존율 계산",
        body="logins(user_id, week).",
        difficulty="Lv5 심화",
        kind="sql",
        expected=["JOIN", "COUNT DISTINCT"],
        hint="week vs week+1."
    ),
    Problem(
        pid="ps_001_basic_select",
        title="특정 컬럼 선택",
        body="df에서 id, ts 컬럼만 선택하세요.",
        difficulty="Lv1 입문",
        kind="pyspark",
        expected=["select"],
        hint="df.select('id','ts')"
    ),
    Problem(
        pid="ps_002_basic_filter",
        title="조건 필터링",
        body="df에서 amount > 100인 행만 남기세요.",
        difficulty="Lv1 입문",
        kind="pyspark",
        expected=["filter"],
        hint="df.filter(col('amount')>100)"
    ),
    Problem(
        pid="ps_003_filter_and_select",
        title="여러 조건 필터링",
        body="df에서 status='OK'이고 ts>2024-01-01인 행의 id만 선택.",
        difficulty="Lv1 입문",
        kind="pyspark",
        expected=["filter","select","&"],
        hint="col 조건 연결."
    ),
    Problem(
        pid="ps_004_groupby_count",
        title="카테고리별 건수",
        body="df(category)에서 category별 count.",
        difficulty="Lv1 입문",
        kind="pyspark",
        expected=["groupBy","count"],
        hint="df.groupBy('category').count()"
    ),
    Problem(
        pid="ps_005_groupby_sum",
        title="월별 매출 합계",
        body="sales(month, amount) 월별 sum(amount).",
        difficulty="Lv1 입문",
        kind="pyspark",
        expected=["groupBy","sum"],
        hint="agg(sum(...))"
    ),
    Problem(
        pid="ps_006_join_basic",
        title="기본 조인",
        body="orders와 customers를 cust_id로 inner join.",
        difficulty="Lv2 초급",
        kind="pyspark",
        expected=["join"],
        hint="orders.join(customers,'cust_id','inner')"
    ),
    Problem(
        pid="ps_007_left_join",
        title="left join 사용",
        body="users.left join purchases.",
        difficulty="Lv2 초급",
        kind="pyspark",
        expected=["join","how='left'"],
        hint="how='left'"
    ),
    Problem(
        pid="ps_008_add_column",
        title="컬럼 추가",
        body="amount>100이면 large=1, else 0 컬럼 추가.",
        difficulty="Lv2 초급",
        kind="pyspark",
        expected=["withColumn","when"],
        hint="withColumn + when"
    ),
    Problem(
        pid="ps_009_remove_duplicates",
        title="중복 제거",
        body="user_id 기준 중복 제거.",
        difficulty="Lv1 입문",
        kind="pyspark",
        expected=["dropDuplicates"],
        hint="df.dropDuplicates(['user_id'])"
    ),
    Problem(
        pid="ps_010_sort_desc",
        title="내림차순 정렬",
        body="amount 기준 desc 정렬.",
        difficulty="Lv1 입문",
        kind="pyspark",
        expected=["orderBy","desc"],
        hint="orderBy(col('amount').desc())"
    ),
    Problem(
        pid="ps_011_window_rank",
        title="카테고리별 rank",
        body="products에서 category별 가격 rank.",
        difficulty="Lv3 중급",
        kind="pyspark",
        expected=["Window","rank"],
        hint="Window.partitionBy."
    ),
    Problem(
        pid="ps_012_window_lag",
        title="이전 값 비교",
        body="orders에서 이전 주문 amount lag.",
        difficulty="Lv3 중급",
        kind="pyspark",
        expected=["lag","Window"],
        hint="lag(...).over(...)"
    ),
    Problem(
        pid="ps_013_window_rows_between",
        title="3개 이동평균",
        body="최근 3개 rowsBetween(-2,0).",
        difficulty="Lv3 중급",
        kind="pyspark",
        expected=["rowsBetween","avg"],
        hint="rolling avg"
    ),
    Problem(
        pid="ps_014_groupby_multi",
        title="2개 컬럼으로 group",
        body="region, category로 묶어 sum(amount).",
        difficulty="Lv2 초급",
        kind="pyspark",
        expected=["groupBy","agg"],
        hint="groupBy 둘 다."
    ),
    Problem(
        pid="ps_015_pivot_status",
        title="상태별 피벗",
        body="logs에서 status pivot count.",
        difficulty="Lv4 고급",
        kind="pyspark",
        expected=["pivot","count"],
        hint="pivot('status').count()"
    ),
    Problem(
        pid="ps_016_weekly_pivot",
        title="주차별 status pivot",
        body="date_trunc로 week 컬럼 만든 뒤 pivot.",
        difficulty="Lv4 고급",
        kind="pyspark",
        expected=["date_trunc","pivot"],
        hint="withColumn week."
    ),
    Problem(
        pid="ps_017_sessionize",
        title="30분 세션 분리",
        body="lag(ts) 비교 후 session_id 누적.",
        difficulty="Lv5 심화",
        kind="pyspark",
        expected=["lag","when","sum over"],
        hint="flag 누적."
    ),
    Problem(
        pid="ps_018_missing_fill",
        title="결측치 채우기",
        body="null amount를 0으로 채우기.",
        difficulty="Lv1 입문",
        kind="pyspark",
        expected=["fillna"],
        hint="df.fillna({'amount':0})"
    ),
    Problem(
        pid="ps_019_type_cast",
        title="타입 변환",
        body="amount를 int로 cast.",
        difficulty="Lv1 입문",
        kind="pyspark",
        expected=["cast"],
        hint="col('amount').cast('int')"
    ),
    Problem(
        pid="ps_020_add_flag_column",
        title="flag 추가",
        body="status='SUCCESS'면 flag=1.",
        difficulty="Lv2 초급",
        kind="pyspark",
        expected=["withColumn","when"],
        hint="CASE WHEN equivalent."
    ),
    Problem(
        pid="ps_021_topn_by_category",
        title="카테고리별 TopN",
        body="Window.rank 후 filter(r<=3).",
        difficulty="Lv3 중급",
        kind="pyspark",
        expected=["rank","Window"],
        hint="rank over partition."
    ),
    Problem(
        pid="ps_022_filter_or_condition",
        title="OR 조건 필터링",
        body="status='FAIL' 또는 amount>1000.",
        difficulty="Lv1 입문",
        kind="pyspark",
        expected=["|","filter"],
        hint="col A | col B"
    ),
    Problem(
        pid="ps_023_groupby_avg",
        title="평균 가격",
        body="products(category, price) category 평균.",
        difficulty="Lv1 입문",
        kind="pyspark",
        expected=["avg"],
        hint="agg(avg)."
    ),
    Problem(
        pid="ps_024_daily_counts",
        title="일별 count",
        body="ts에서 date 추출 후 groupBy.",
        difficulty="Lv1 입문",
        kind="pyspark",
        expected=["to_date"],
        hint="withColumn(to_date)."
    ),
    Problem(
        pid="ps_025_user_last_login",
        title="최근 로그인",
        body="max(ts) groupBy user.",
        difficulty="Lv1 입문",
        kind="pyspark",
        expected=["max"],
        hint="agg(max)."
    ),
    Problem(
        pid="ps_026_top_cities",
        title="도시별 사용자 수 desc",
        body="users(city).",
        difficulty="Lv1 입문",
        kind="pyspark",
        expected=["count","orderBy"],
        hint="desc."
    ),
    Problem(
        pid="ps_027_anomaly_amount",
        title="이상치 탐지",
        body="amount > avg+2*std.",
        difficulty="Lv4 고급",
        kind="pyspark",
        expected=["agg","stddev"],
        hint="collect avg&std or window."
    ),
    Problem(
        pid="ps_028_groupby_min_max",
        title="최소/최대 동시에",
        body="groupBy category로 min/max price.",
        difficulty="Lv1 입문",
        kind="pyspark",
        expected=["min","max"],
        hint="agg(min,max)."
    ),
    Problem(
        pid="ps_029_window_percent_rank",
        title="퍼센트 순위",
        body="percent_rank over partition.",
        difficulty="Lv4 고급",
        kind="pyspark",
        expected=["percent_rank","Window"],
        hint="Window.orderBy."
    ),
    Problem(
        pid="ps_030_read_parquet",
        title="파케 읽기",
        body="spark.read.parquet.",
        difficulty="Lv1 입문",
        kind="pyspark",
        expected=["spark.read"],
        hint="parquet path."
    ),
    Problem(
        pid="ps_031_write_parquet",
        title="파케 저장",
        body="df.write.parquet.",
        difficulty="Lv1 입문",
        kind="pyspark",
        expected=["write"],
        hint="coalesce(1)."
    ),
    Problem(
        pid="ps_032_to_json",
        title="JSON 변환",
        body="to_json struct.",
        difficulty="Lv3 중급",
        kind="pyspark",
        expected=["to_json","struct"],
        hint="withColumn."
    ),
    Problem(
        pid="ps_033_bucketize",
        title="범주화",
        body="age bucket 0-20/20-40/40+. ",
        difficulty="Lv2 초급",
        kind="pyspark",
        expected=["when","withColumn"],
        hint="CASE WHEN."
    ),
    Problem(
        pid="ps_034_moving_sum",
        title="이동합",
        body="5-row rolling sum.",
        difficulty="Lv3 중급",
        kind="pyspark",
        expected=["rowsBetween","sum"],
        hint="Window.rowsBetween."
    ),
    Problem(
        pid="ps_035_user_gap_days",
        title="로그인 gap",
        body="lag(ts)→datediff.",
        difficulty="Lv3 중급",
        kind="pyspark",
        expected=["lag","datediff"],
        hint="datediff(ts,lag)."
    ),
    Problem(
        pid="ps_036_nested_struct",
        title="struct 생성",
        body="user struct(name, age).",
        difficulty="Lv2 초급",
        kind="pyspark",
        expected=["struct"],
        hint="df.select(struct(...))"
    ),
    Problem(
        pid="ps_037_explode_array",
        title="배열 explode",
        body="explode(tags).",
        difficulty="Lv2 초급",
        kind="pyspark",
        expected=["explode"],
        hint="from pyspark.sql.functions."
    ),
    Problem(
        pid="ps_038_collect_list",
        title="리스트 집계",
        body="user별 event collect_list.",
        difficulty="Lv3 중급",
        kind="pyspark",
        expected=["collect_list"],
        hint="agg."
    ),
    Problem(
        pid="ps_039_nunique_users",
        title="unique count",
        body="approx_count_distinct.",
        difficulty="Lv2 초급",
        kind="pyspark",
        expected=["approx_count_distinct"],
        hint="agg(...)."
    ),
    Problem(
        pid="ps_040_hash_column",
        title="해시값 생성",
        body="sha2(email,256).",
        difficulty="Lv2 초급",
        kind="pyspark",
        expected=["sha2"],
        hint="withColumn."
    ),
    Problem(
        pid="ps_041_groupby_std",
        title="카테고리별 표준편차",
        body="stddev.",
        difficulty="Lv2 초급",
        kind="pyspark",
        expected=["stddev"],
        hint="agg(stddev)."
    ),
    Problem(
        pid="ps_042_bucketized_dates",
        title="주간 bucket",
        body="date_trunc('week').",
        difficulty="Lv1 입문",
        kind="pyspark",
        expected=["date_trunc"],
        hint="week column."
    ),
    Problem(
        pid="ps_043_json_parse",
        title="JSON 컬럼 파싱",
        body="from_json 적용.",
        difficulty="Lv4 고급",
        kind="pyspark",
        expected=["from_json","schema"],
        hint="schema 필요."
    ),
    Problem(
        pid="ps_044_top_k_by_window",
        title="윈도우 TopK",
        body="dense_rank over.",
        difficulty="Lv3 중급",
        kind="pyspark",
        expected=["dense_rank"],
        hint="dense_rank().over(...)"
    ),
    Problem(
        pid="ps_045_groupby_ratio",
        title="비율 계산",
        body="amount / sum(amount) over().",
        difficulty="Lv3 중급",
        kind="pyspark",
        expected=["window sum"],
        hint="over()."
    ),
    Problem(
        pid="ps_046_remove_outliers",
        title="IQR 이상치 제거",
        body="Q1/Q3 계산 후 filter.",
        difficulty="Lv5 심화",
        kind="pyspark",
        expected=["percentile_approx"],
        hint="collect percentile."
    ),
    Problem(
        pid="ps_047_user_first_event",
        title="첫 이벤트",
        body="row_number rn=1.",
        difficulty="Lv3 중급",
        kind="pyspark",
        expected=["row_number","Window"],
        hint="orderBy ts."
    ),
    Problem(
        pid="ps_048_user_last_event",
        title="마지막 이벤트",
        body="orderBy desc rn=1.",
        difficulty="Lv3 중급",
        kind="pyspark",
        expected=["row_number"],
        hint="desc."
    ),
    Problem(
        pid="ps_049_groupby_multiple_aggs",
        title="여러 집계 계산",
        body="sum, avg, count 동시에.",
        difficulty="Lv2 초급",
        kind="pyspark",
        expected=["agg"],
        hint="agg(sum(...),avg(...))."
    ),
    Problem(
        pid="ps_050_complex_sessionize",
        title="복합 세션 규칙",
        body="5분/10분 조건 혼합 세션화.",
        difficulty="Lv5 심화",
        kind="pyspark",
        expected=["lag","when","cumulative sum"],
        hint="다중 flag 누적."
    ),
    Problem(
        pid="pc_001_load_filter",
        title="데이터 로드 후 필터링",
        body="data.csv를 로드하고 amount>100인 행만 남기는 pseudocode.",
        difficulty="Lv1 입문",
        kind="pseudocode",
        expected=["load","filter"],
        hint="load → filter."
    ),
    Problem(
        pid="pc_002_groupby_sum",
        title="카테고리별 합계",
        body="category 기준 amount 합계 pseudocode.",
        difficulty="Lv1 입문",
        kind="pseudocode",
        expected=["group","sum"],
        hint="group then sum."
    ),
    Problem(
        pid="pc_003_join_two_lists",
        title="두 데이터 조인",
        body="users와 orders를 user_id로 join하는 pseudocode.",
        difficulty="Lv2 초급",
        kind="pseudocode",
        expected=["join","key"],
        hint="loop matching keys."
    ),
    Problem(
        pid="pc_004_window_last3",
        title="최근 3개 평균",
        body="amount 리스트에서 최근 3개 rolling avg.",
        difficulty="Lv3 중급",
        kind="pseudocode",
        expected=["window","for"],
        hint="i-2~i window."
    ),
    Problem(
        pid="pc_005_find_max",
        title="최대값 찾기",
        body="리스트에서 가장 큰 값을 찾으세요.",
        difficulty="Lv1 입문",
        kind="pseudocode",
        expected=["loop","max"],
        hint="max = 0."
    ),
    Problem(
        pid="pc_006_daily_event_count",
        title="일별 count 계산",
        body="ts 리스트에서 day 기준 count.",
        difficulty="Lv2 초급",
        kind="pseudocode",
        expected=["dict","increment"],
        hint="hash map."
    ),
    Problem(
        pid="pc_007_session_flag",
        title="세션 나누기",
        body="ts diff>30min이면 session+1.",
        difficulty="Lv4 고급",
        kind="pseudocode",
        expected=["lag","if","counter"],
        hint="session_id++."
    ),
    Problem(
        pid="pc_008_anomaly_detect",
        title="평균 대비 2배 이상 탐지",
        body="values 중 avg*2 초과.",
        difficulty="Lv2 초급",
        kind="pseudocode",
        expected=["avg","if"],
        hint="compute avg then scan."
    ),
    Problem(
        pid="pc_009_pipeline_ingest_clean",
        title="ETL 파이프라인",
        body="load→clean→join→aggregate 순 pseudocode.",
        difficulty="Lv3 중급",
        kind="pseudocode",
        expected=["steps"],
        hint="define 4 steps."
    ),
    Problem(
        pid="pc_010_fraud_rules",
        title="간단 사기 rule set",
        body="amount>1000 AND country='X' 라면 flag.",
        difficulty="Lv3 중급",
        kind="pseudocode",
        expected=["if","and"],
        hint="rule check."
    ),
    Problem(
        pid="pc_011_rank_users",
        title="점수 기반 순위",
        body="user score 리스트를 내림차순 정렬.",
        difficulty="Lv2 초급",
        kind="pseudocode",
        expected=["sort"],
        hint="sort desc."
    ),
    Problem(
        pid="pc_012_top_k",
        title="상위 K개 찾기",
        body="리스트에서 상위 3개 값.",
        difficulty="Lv2 초급",
        kind="pseudocode",
        expected=["sort","slice"],
        hint="sort then pick."
    ),
    Problem(
        pid="pc_013_moving_std",
        title="이동 표준편차",
        body="값 리스트에서 5개 윈도우 std.",
        difficulty="Lv4 고급",
        kind="pseudocode",
        expected=["window","std"],
        hint="std formula."
    ),
    Problem(
        pid="pc_014_min_max_normalize",
        title="0~1 정규화",
        body="values에서 (x-min)/(max-min).",
        difficulty="Lv2 초급",
        kind="pseudocode",
        expected=["min","max"],
        hint="two-pass."
    ),
    Problem(
        pid="pc_015_deduplicate",
        title="중복 제거",
        body="id 중복 삭제.",
        difficulty="Lv1 입문",
        kind="pseudocode",
        expected=["set"],
        hint="visited set."
    ),
    Problem(
        pid="pc_016_build_index",
        title="인덱스 맵 생성",
        body="user_id를 key로 event 리스트 저장.",
        difficulty="Lv3 중급",
        kind="pseudocode",
        expected=["dict","append"],
        hint="grouping."
    ),
    Problem(
        pid="pc_017_pipeline_stream",
        title="스트림 처리",
        body="새 이벤트마다 validate→enrich→store.",
        difficulty="Lv4 고급",
        kind="pseudocode",
        expected=["loop","function"],
        hint="on event."
    ),
    Problem(
        pid="pc_018_label_encoder",
        title="범주형 변환",
        body="category→index 매핑.",
        difficulty="Lv2 초급",
        kind="pseudocode",
        expected=["map"],
        hint="assign integer."
    ),
    Problem(
        pid="pc_019_histogram",
        title="히스토그램 계산",
        body="bins에 count.",
        difficulty="Lv2 초급",
        kind="pseudocode",
        expected=["ranges","increment"],
        hint="bin loop."
    ),
    Problem(
        pid="pc_020_user_timeline",
        title="타임라인 정렬",
        body="이벤트 ts로 sort 후 출력.",
        difficulty="Lv1 입문",
        kind="pseudocode",
        expected=["sort"],
        hint="ts ascending."
    ),
    Problem(
        pid="pc_021_running_total",
        title="누적합",
        body="values 누적합.",
        difficulty="Lv1 입문",
        kind="pseudocode",
        expected=["loop","sum"],
        hint="running_sum."
    ),
    Problem(
        pid="pc_022_merge_sorted_lists",
        title="정렬 리스트 병합",
        body="두 리스트 merge.",
        difficulty="Lv4 고급",
        kind="pseudocode",
        expected=["two pointers"],
        hint="i/j pointers."
    ),
    Problem(
        pid="pc_023_detect_spikes",
        title="스파이크 탐지",
        body="value > 평균+3표준편차.",
        difficulty="Lv3 중급",
        kind="pseudocode",
        expected=["mean","std"],
        hint="check threshold."
    ),
    Problem(
        pid="pc_024_build_cooccurrence",
        title="동시 등장 매트릭스",
        body="basket→pair count.",
        difficulty="Lv5 심화",
        kind="pseudocode",
        expected=["nested loop"],
        hint="pairs."
    ),
    Problem(
        pid="pc_025_limit_throughput",
        title="처리량 제한",
        body="초당 100건 이하로 처리.",
        difficulty="Lv4 고급",
        kind="pseudocode",
        expected=["sleep","counter"],
        hint="rate limit."
    ),
    Problem(
        pid="pc_026_retry_logic",
        title="3회 재시도 로직",
        body="실패 시 최대 3회 retry.",
        difficulty="Lv3 중급",
        kind="pseudocode",
        expected=["loop","break"],
        hint="retry count."
    ),
    Problem(
        pid="pc_027_partition_by_key",
        title="키 기반 파티션",
        body="user_id mod N으로 분배.",
        difficulty="Lv3 중급",
        kind="pseudocode",
        expected=["mod"],
        hint="shard."
    ),
    Problem(
        pid="pc_028_cache_layer",
        title="캐시 사용",
        body="cache miss면 DB 조회 후 저장.",
        difficulty="Lv4 고급",
        kind="pseudocode",
        expected=["cache","fallback"],
        hint="cache-first."
    ),
    Problem(
        pid="pc_029_rolling_min",
        title="이동 최소",
        body="window min.",
        difficulty="Lv3 중급",
        kind="pseudocode",
        expected=["window"],
        hint="sliding window."
    ),
    Problem(
        pid="pc_030_top_users_by_score",
        title="score top5",
        body="sort→slice.",
        difficulty="Lv1 입문",
        kind="pseudocode",
        expected=["sort"],
        hint="desc."
    ),
    Problem(
        pid="pc_031_find_median",
        title="중앙값",
        body="sort 후 mid.",
        difficulty="Lv2 초급",
        kind="pseudocode",
        expected=["sort"],
        hint="len//2."
    ),
    Problem(
        pid="pc_032_fault_tolerance",
        title="예외 복구",
        body="try→catch→log→continue.",
        difficulty="Lv3 중급",
        kind="pseudocode",
        expected=["try","catch"],
        hint="exception."
    ),
    Problem(
        pid="pc_033_data_sharding",
        title="데이터 샤딩",
        body="N개 shard에 key 기반 분배.",
        difficulty="Lv4 고급",
        kind="pseudocode",
        expected=["mod","route"],
        hint="shard_id."
    ),
    Problem(
        pid="pc_034_detect_duplicates",
        title="중복 데이터 식별",
        body="seen set에 존재하면 duplicate.",
        difficulty="Lv1 입문",
        kind="pseudocode",
        expected=["set"],
        hint="seen.add."
    ),
    Problem(
        pid="pc_035_resample_daily",
        title="daily resampling",
        body="ts→day group.",
        difficulty="Lv3 중급",
        kind="pseudocode",
        expected=["group"],
        hint="day key."
    ),
    Problem(
        pid="pc_036_stream_window_agg",
        title="스트림 윈도우 집계",
        body="5분 window count.",
        difficulty="Lv4 고급",
        kind="pseudocode",
        expected=["window"],
        hint="time bucket."
    ),
    Problem(
        pid="pc_037_key_value_store",
        title="KV 저장소",
        body="put/get pseudocode.",
        difficulty="Lv2 초급",
        kind="pseudocode",
        expected=["dict"],
        hint="key lookup."
    ),
    Problem(
        pid="pc_038_sort_by_two_keys",
        title="2개 기준 정렬",
        body="score desc, ts asc.",
        difficulty="Lv2 초급",
        kind="pseudocode",
        expected=["sort"],
        hint="tuple sort."
    ),
    Problem(
        pid="pc_039_trace_pipeline",
        title="파이프라인 단계 추적",
        body="step1→step2→step3 로그.",
        difficulty="Lv2 초급",
        kind="pseudocode",
        expected=["log"],
        hint="print step."
    ),
    Problem(
        pid="pc_040_alert_threshold",
        title="임계치 alert",
        body="value>threshold이면 alert.",
        difficulty="Lv1 입문",
        kind="pseudocode",
        expected=["if"],
        hint="simple check."
    ),
    Problem(
        pid="pc_041_batch_processing",
        title="배치 처리 loop",
        body="records batch 단위 처리.",
        difficulty="Lv3 중급",
        kind="pseudocode",
        expected=["for","chunks"],
        hint="for i+=batch."
    ),
    Problem(
        pid="pc_042_stepwise_enrichment",
        title="데이터 정제/변환/보강",
        body="clean→normalize→enrich.",
        difficulty="Lv3 중급",
        kind="pseudocode",
        expected=["pipeline"],
        hint="define functions."
    ),
    Problem(
        pid="pc_043_join_multiple_sources",
        title="3개 소스 join",
        body="src1→src2→src3 순 join.",
        difficulty="Lv4 고급",
        kind="pseudocode",
        expected=["join","multi-stage"],
        hint="incremental join."
    ),
    Problem(
        pid="pc_044_priority_queue",
        title="우선순위 큐 사용",
        body="highest priority pop.",
        difficulty="Lv5 심화",
        kind="pseudocode",
        expected=["heap"],
        hint="push/pop."
    ),
    Problem(
        pid="pc_045_backfill_missing",
        title="누락값 백필",
        body="missing→forward fill.",
        difficulty="Lv3 중급",
        kind="pseudocode",
        expected=["loop","previous value"],
        hint="carry value."
    ),
    Problem(
        pid="pc_046_delta_processing",
        title="증분 처리",
        body="last_ts 이후 데이터만 처리.",
        difficulty="Lv4 고급",
        kind="pseudocode",
        expected=["filter"],
        hint="if ts>last."
    ),
    Problem(
        pid="pc_047_parallel_workers",
        title="병렬 작업 분배",
        body="workers N개에 round-robin 분배.",
        difficulty="Lv4 고급",
        kind="pseudocode",
        expected=["mod"],
        hint="i mod N."
    ),
    Problem(
        pid="pc_048_rolling_corr",
        title="이동 상관계수",
        body="window correlation.",
        difficulty="Lv5 심화",
        kind="pseudocode",
        expected=["window","corr"],
        hint="calc corr."
    ),
    Problem(
        pid="pc_049_metadata_schema",
        title="메타데이터 스키마 관리",
        body="tables list→schema dict.",
        difficulty="Lv3 중급",
        kind="pseudocode",
        expected=["schema"],
        hint="map table→schema."
    ),
    Problem(
        pid="pc_050_feature_engineering",
        title="특성 생성 로직",
        body="original features → derived features.",
        difficulty="Lv4 고급",
        kind="pseudocode",
        expected=["transform"],
        hint="define feature funcs."
    ),
    Problem(
        pid="dc_001_flood_response",
        title="홍수 대응 시스템 구축",
        body="도시 홍수 발생 시 데이터를 활용해 어디에 자원을 배치할지 결정하는 Decomposition.",
        difficulty="Lv5 심화",
        kind="decomp",
        expected=["entities","metrics","execution"],
        hint="shelters, roads, sensors."
    ),
    Problem(
        pid="dc_002_earthquake_supply",
        title="지진 구호 물자 배분",
        body="피해 지역별 수요/공급/우선순위 기반 routing 설계.",
        difficulty="Lv5 심화",
        kind="decomp",
        expected=["table schema","MVP","value"],
        hint="demand vs supply."
    ),
    Problem(
        pid="dc_003_opioid_fraud",
        title="오피오이드 처방 사기 탐지",
        body="의사/환자/처방 패턴으로 사기 식별.",
        difficulty="Lv5 심화",
        kind="decomp",
        expected=["joins","patterns","signals"],
        hint="outlier doctors."
    ),
    Problem(
        pid="dc_004_illegal_firearms",
        title="불법 총기 탐지",
        body="우편 소포 데이터 기반 위험 패턴 식별.",
        difficulty="Lv5 심화",
        kind="decomp",
        expected=["features","flags","routing"],
        hint="parcel metadata."
    ),
    Problem(
        pid="dc_005_insider_trading",
        title="내부자 거래 탐지",
        body="직원 커뮤니케이션 + 거래 로그 분석.",
        difficulty="Lv5 심화",
        kind="decomp",
        expected=["correlation","timeline"],
        hint="unusual patterns."
    ),
    Problem(
        pid="dc_006_traffic_congestion",
        title="교통 체증 완화 시스템",
        body="센서/차량/도로 이벤트 기반 최적 경로 제안.",
        difficulty="Lv4 고급",
        kind="decomp",
        expected=["schema","metrics"],
        hint="edge speed."
    ),
    Problem(
        pid="dc_007_supply_chain_risk",
        title="공급망 리스크 탐지",
        body="supplier/region/inventory 기반 위험 조기 발견.",
        difficulty="Lv4 고급",
        kind="decomp",
        expected=["risk score"],
        hint="multi-source."
    ),
    Problem(
        pid="dc_008_energy_grid_outage",
        title="전력 그리드 outage 예측",
        body="센서+기상 데이터 기반 위험 지역 예측.",
        difficulty="Lv5 심화",
        kind="decomp",
        expected=["signals"],
        hint="time series."
    ),
    Problem(
        pid="dc_009_hospital_triage",
        title="응급실 환자 대기 최적화",
        body="환자 severity + capacity 기반 triage.",
        difficulty="Lv4 고급",
        kind="decomp",
        expected=["priority","constraints"],
        hint="queue design."
    ),
    Problem(
        pid="dc_010_cyber_intrusion",
        title="사이버 침입 탐지",
        body="로그 이벤트 기반 이상 접근 탐지.",
        difficulty="Lv5 심화",
        kind="decomp",
        expected=["signals","threshold"],
        hint="ip/user patterns."
    ),
    Problem(
        pid="dc_011_water_quality",
        title="수질 이상 탐지",
        body="센서 값 기반 품질 문제 조기 탐지.",
        difficulty="Lv4 고급",
        kind="decomp",
        expected=["threshold"],
        hint="ph/turbidity."
    ),
    Problem(
        pid="dc_012_public_transport_planning",
        title="대중교통 노선 최적화",
        body="승차/하차 패턴 기반 route 개선.",
        difficulty="Lv4 고급",
        kind="decomp",
        expected=["flows"],
        hint="hourly usage."
    ),
    Problem(
        pid="dc_013_emergency_dispatch",
        title="긴급 차량 배차",
        body="incident location + availability 기반.",
        difficulty="Lv5 심화",
        kind="decomp",
        expected=["routing"],
        hint="response time."
    ),
    Problem(
        pid="dc_014_water_leak_detection",
        title="수도관 누수 탐지",
        body="압력/유량 데이터 이상 탐지.",
        difficulty="Lv4 고급",
        kind="decomp",
        expected=["signals"],
        hint="spikes."
    ),
    Problem(
        pid="dc_015_ecommerce_reco",
        title="추천 시스템 설계",
        body="user-item-event schema 기반.",
        difficulty="Lv3 중급",
        kind="decomp",
        expected=["features"],
        hint="user embedding."
    ),
    Problem(
        pid="dc_016_financial_anomaly",
        title="금융거래 이상 탐지",
        body="amount/frequency/region 기반.",
        difficulty="Lv4 고급",
        kind="decomp",
        expected=["signals"],
        hint="multi-factor."
    ),
    Problem(
        pid="dc_017_border_security",
        title="국경 불법 이동 탐지",
        body="센서/카메라/위치 패턴.",
        difficulty="Lv5 심화",
        kind="decomp",
        expected=["joins"],
        hint="trajectory."
    ),
    Problem(
        pid="dc_018_infrastructure_monitor",
        title="시설물 상태 모니터링",
        body="센서 진동/온도 기반.",
        difficulty="Lv4 고급",
        kind="decomp",
        expected=["threshold"],
        hint="trend changes."
    ),
    Problem(
        pid="dc_019_healthcare_claims",
        title="의료 클레임 사기 탐지",
        body="병원/의사/환자/청구 패턴.",
        difficulty="Lv5 심화",
        kind="decomp",
        expected=["metrics"],
        hint="abnormal clusters."
    ),
    Problem(
        pid="dc_020_food_safety",
        title="식품 안전 이상 탐지",
        body="inspection+temperature 기록.",
        difficulty="Lv4 고급",
        kind="decomp",
        expected=["signals"],
        hint="violations."
    ),
    Problem(
        pid="dc_021_fire_dispatch",
        title="화재 대응 배치",
        body="risk score 기반 resource 위치.",
        difficulty="Lv4 고급",
        kind="decomp",
        expected=["score"],
        hint="wind direction."
    ),
    Problem(
        pid="dc_022_illegal_fishing",
        title="불법 어업 탐지",
        body="GPS 경로 이상 탐지.",
        difficulty="Lv5 심화",
        kind="decomp",
        expected=["trajectory","rules"],
        hint="restricted zones."
    ),
    Problem(
        pid="dc_023_toll_fraud",
        title="통행료 사기 탐지",
        body="차량 plate + timestamp.",
        difficulty="Lv4 고급",
        kind="decomp",
        expected=["sequence"],
        hint="impossible speeds."
    ),
    Problem(
        pid="dc_024_education_dropout",
        title="학생 중도 이탈 예측",
        body="attendance/grades/engagement.",
        difficulty="Lv3 중급",
        kind="decomp",
        expected=["features"],
        hint="risk factor."
    ),
    Problem(
        pid="dc_025_mail_sorting_optimization",
        title="우편물 분류 최적화",
        body="zip code routing.",
        difficulty="Lv3 중급",
        kind="decomp",
        expected=["tables"],
        hint="routes."
    ),
    Problem(
        pid="dc_026_ev_charging",
        title="전기차 충전소 배치",
        body="traffic+population 패턴.",
        difficulty="Lv4 고급",
        kind="decomp",
        expected=["demand"],
        hint="geo usage."
    ),
    Problem(
        pid="dc_027_border_wait_time",
        title="국경 대기시간 예측",
        body="entry logs/time/weather.",
        difficulty="Lv4 고급",
        kind="decomp",
        expected=["window"],
        hint="queue length."
    ),
    Problem(
        pid="dc_028_insurance_risk",
        title="보험 리스크 분석",
        body="claim frequency+severity.",
        difficulty="Lv3 중급",
        kind="decomp",
        expected=["severity"],
        hint="multi-factor."
    ),
    Problem(
        pid="dc_029_metro_flow",
        title="지하철 승객 흐름 분석",
        body="tap-in/out event.",
        difficulty="Lv4 고급",
        kind="decomp",
        expected=["flow"],
        hint="time slices."
    ),
    Problem(
        pid="dc_030_illegal_dumping",
        title="불법 폐기물 탐지",
        body="sensor+location patterns.",
        difficulty="Lv5 심화",
        kind="decomp",
        expected=["signals"],
        hint="suspicious trips."
    ),
    Problem(
        pid="dc_031_public_health_surveillance",
        title="감염병 조기 탐지",
        body="hospital visits/symptoms.",
        difficulty="Lv5 심화",
        kind="decomp",
        expected=["signals"],
        hint="clusters."
    ),
    Problem(
        pid="dc_032_maritime_smuggling",
        title="해상 밀수 탐지",
        body="AIS tracks pattern.",
        difficulty="Lv5 심화",
        kind="decomp",
        expected=["trajectory"],
        hint="loitering zones."
    ),
    Problem(
        pid="dc_033_crop_yield_forecast",
        title="농작물 수확량 예측",
        body="soil+weather+satellite.",
        difficulty="Lv4 고급",
        kind="decomp",
        expected=["features"],
        hint="multi-source."
    ),
    Problem(
        pid="dc_034_food_delivery_eta",
        title="배달 ETA 예측",
        body="driver+distance+traffic.",
        difficulty="Lv3 중급",
        kind="decomp",
        expected=["metrics"],
        hint="order-level."
    ),
    Problem(
        pid="dc_035_warehouse_slotting",
        title="창고 재고 배치",
        body="SKU picking frequency.",
        difficulty="Lv4 고급",
        kind="decomp",
        expected=["frequency"],
        hint="ABC analysis."
    ),
    Problem(
        pid="dc_036_pipeline_monitor",
        title="파이프라인 누유 탐지",
        body="pressure/time anomalies.",
        difficulty="Lv5 심화",
        kind="decomp",
        expected=["signals"],
        hint="spikes/drops."
    ),
    Problem(
        pid="dc_037_bus_schedule_opt",
        title="버스 배차 최적화",
        body="demand by hour.",
        difficulty="Lv3 중급",
        kind="decomp",
        expected=["demand"],
        hint="capacity."
    ),
    Problem(
        pid="dc_038_retail_stockout",
        title="품절 예측",
        body="sales velocity.",
        difficulty="Lv3 중급",
        kind="decomp",
        expected=["velocity"],
        hint="days of supply."
    ),
    Problem(
        pid="dc_039_parking_occupancy",
        title="주차장 점유율 예측",
        body="entry/exit logs.",
        difficulty="Lv3 중급",
        kind="decomp",
        expected=["delta"],
        hint="net entries."
    ),
    Problem(
        pid="dc_040_port_congestion",
        title="항만 혼잡 탐지",
        body="ship arrivals/loading time.",
        difficulty="Lv5 심화",
        kind="decomp",
        expected=["queue"],
        hint="turnaround."
    ),
    Problem(
        pid="dc_041_smoke_detection",
        title="연기 감지",
        body="sensor spectrum patterns.",
        difficulty="Lv4 고급",
        kind="decomp",
        expected=["threshold"],
        hint="multi-sensor."
    ),
    Problem(
        pid="dc_042_vehicle_maintenance",
        title="차량 고장 예측",
        body="engine/sensor readings.",
        difficulty="Lv4 고급",
        kind="decomp",
        expected=["features"],
        hint="degradation curve."
    ),
    Problem(
        pid="dc_043_hotel_demand",
        title="호텔 수요 예측",
        body="check-in patterns.",
        difficulty="Lv3 중급",
        kind="decomp",
        expected=["seasonality"],
        hint="event days."
    ),
    Problem(
        pid="dc_044_loan_default",
        title="대출 연체 위험",
        body="income/debt/payment pattern.",
        difficulty="Lv5 심화",
        kind="decomp",
        expected=["signals"],
        hint="risk scoring."
    ),
    Problem(
        pid="dc_045_smart_meter_fraud",
        title="전력 계량기 조작 탐지",
        body="energy usage anomalies.",
        difficulty="Lv5 심화",
        kind="decomp",
        expected=["patterns"],
        hint="tampering."
    ),
    Problem(
        pid="dc_046_taxi_demand_heatmap",
        title="택시 수요 히트맵",
        body="geo+time heatmap.",
        difficulty="Lv3 중급",
        kind="decomp",
        expected=["bins"],
        hint="grid."
    ),
    Problem(
        pid="dc_047_air_quality_alerts",
        title="대기질 경보",
        body="pm2.5/ozone spikes.",
        difficulty="Lv3 중급",
        kind="decomp",
        expected=["threshold"],
        hint="alerts."
    ),
    Problem(
        pid="dc_048_building_energy",
        title="건물 에너지 사용 최적화",
        body="HVAC usage patterns.",
        difficulty="Lv4 고급",
        kind="decomp",
        expected=["signals"],
        hint="baseline vs current."
    ),
    Problem(
        pid="dc_049_emergency_hospital_load",
        title="병원 부하 예측",
        body="arrival rate.",
        difficulty="Lv4 고급",
        kind="decomp",
        expected=["lambda"],
        hint="queue model."
    ),
    Problem(
        pid="dc_050_mail_anomaly",
        title="특이 우편물 탐지",
        body="weight/size/route patterns.",
        difficulty="Lv5 심화",
        kind="decomp",
        expected=["anomaly signals"],
        hint="unusual routes."
    ),
]
