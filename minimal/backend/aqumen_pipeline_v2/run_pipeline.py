from aqumen_pipeline.pipeline.orchestrator import Orchestrator


def main():
    orch = Orchestrator()
    topic = "LLM Post-Training with DPO"
    ok1, cats, _ = orch.step1(topic)
    if not ok1:
        print("Step 1 failed.")
        return
    subtopic = cats.get("Intermediate", ["General concepts"])[0]
    ok2, catalog, _ = orch.step2(topic, subtopic, "Intermediate")
    if not ok2:
        print("Step 2 failed.")
        return
    ok3, question, _ = orch.step3(topic, subtopic, "Intermediate", catalog, previous_failures=[])
    if not ok3:
        print("Step 3 failed.")
        return
    s4_ok, mid_text, _ = orch.step4(question)
    s5_ok, weak_text, _ = orch.step5(question)
    s6_ok, judge, _ = orch.step6(question, catalog, mid_text, weak_text)
    s7_ok, assess, _ = orch.step7(topic, subtopic, question, mid_text, weak_text, judge)
    orch.mark_end([], differentiation=bool(judge.get("differentiation_achieved")) if isinstance(judge, dict) else False, final_success=bool(s7_ok))
    print("Run complete (see logs/ and results/).")

if __name__ == "__main__":
    main()
