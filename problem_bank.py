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
]
