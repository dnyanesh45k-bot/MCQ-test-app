import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="MCQ Test App", layout="centered")

st.title("🧠 MCQ Test Application (Timed + Navigation)")

st.write("Upload a CSV file with columns: Question, OptionA, OptionB, OptionC, OptionD, Correct")
uploaded_file = st.file_uploader("Upload your MCQ file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    total_questions = len(df)
    time_per_question = 108  # 1.8 minutes per question = 108 seconds
    total_time = total_questions * time_per_question

    # Initialize session state
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()
        st.session_state.current_question = 0
        st.session_state.answers = {}
        st.session_state.submitted = False
        st.session_state.auto_submitted = False

    elapsed_time = int(time.time() - st.session_state.start_time)
    remaining_time = total_time - elapsed_time

    # Auto-submit if time runs out
    if remaining_time <= 0 and not st.session_state.submitted:
        st.session_state.submitted = True
        st.session_state.auto_submitted = True

    # Display timer
    if not st.session_state.submitted:
        minutes = remaining_time // 60
        seconds = remaining_time % 60
        st.markdown(f"⏳ **Time Remaining:** {minutes:02d}:{seconds:02d}")
        st.progress(remaining_time / total_time)

    # --- Navigation Buttons (Jump to any question) ---
    st.markdown("### 📍 Jump to Question:")
    cols = st.columns(min(total_questions, 10))
    for i in range(total_questions):
        col = cols[i % 10]
        if col.button(str(i + 1), key=f"jump{i}"):
            st.session_state.current_question = i

    # --- Question Display Section ---
    current = st.session_state.current_question

    if not st.session_state.submitted:
        question_data = df.iloc[current]
        st.markdown(f"### Question {current + 1} of {total_questions}")
        st.write(question_data["Question"])

        options = [
            question_data["OptionA"],
            question_data["OptionB"],
            question_data["OptionC"],
            question_data["OptionD"]
        ]
        options = [opt for opt in options if pd.notna(opt) and opt != "-"]

        selected = st.radio(
            "Select your answer:",
            options,
            index=options.index(st.session_state.answers.get(current))
            if current in st.session_state.answers else 0,
            key=f"q{current}"
        )

        st.session_state.answers[current] = selected

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⬅️ Previous", disabled=current == 0):
                st.session_state.current_question -= 1
        with col2:
            if st.button("➡️ Next", disabled=current == total_questions - 1):
                st.session_state.current_question += 1
        with col3:
            if st.button("✅ Submit"):
                st.session_state.submitted = True

        # Refresh every second for timer updates
        time.sleep(1)
        st.experimental_rerun()

    # --- Results Section ---
    else:
        st.subheader("📊 Test Completed!")
        if st.session_state.auto_submitted:
            st.warning("⏰ Time’s up! Your test was auto-submitted.")

        score = 0
        for i, row in df.iterrows():
            correct_answer = row[f"Option{row['Correct']}"]
            user_answer = st.session_state.answers.get(i, "")
            if user_answer == correct_answer:
                score += 1
                st.success(f"Q{i+1}: ✅ Correct")
            else:
                st.error(f"Q{i+1}: ❌ Wrong (Your answer: {user_answer} | Correct: {correct_answer})")

        st.markdown(f"### 🏁 Final Score: **{score}/{total_questions}** ({score/total_questions*100:.2f}%)")