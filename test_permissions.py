from src.check_permission import check_secret_permission

# ✏️ 在这里配置你要测试的身份信息与意图
test_cases = [
    {
        "persona": "junshi",  # 军师
        "intent": {
            "intent_type": "read_memory"
        },
        "secret": "junshi_secret"
    },
    {
        "persona": "lockling",  # 锁灵
        "intent": {
            "intent_type": "write_customers"
        },
        "secret": "lockling_secret"
    },
    {
        "persona": "yuheng",  # 玉衡
        "intent": {
            "intent_type": "read_finance"
        },
        "secret": "yuheng_secret"
    },
    {
        "persona": "silin",  # 司铃
        "intent": {
            "intent_type": "write_plan"
        },
        "secret": "silin_secret"
    },
    {
        "persona": "lockling",
        "intent": {
            "intent_type": "chitchat"  # 默认意图
        },
        "secret": "wrong_secret"
    }
]

# ✅ 运行所有测试
if __name__ == "__main__":
    for idx, case in enumerate(test_cases):
        print(f"\n--- 测试用例 {idx + 1} ---")
        result = check_secret_permission(
            intent=case["intent"],
            persona=case["persona"],
            secret=case["secret"]
        )
        print(f"Persona: {case['persona']}")
        print(f"Intent Type: {case['intent']['intent_type']}")
        print(f"结果: {'✅ 允许' if result['allow'] else '❌ 拒绝'}")
        print(f"原因: {result['reason']}")
        print(f"附加信息: {result}")
