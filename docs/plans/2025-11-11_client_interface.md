# PRD: Greek Grammar Practice - Client Interface

## 1. Introduction/Overview

This document outlines the requirements for a web-based client application designed to help learners of Greek practice their grammar skills. The initial version of this application will focus on providing an endless supply of interactive, textbook-style exercises. The first and only exercise in this version will be a "Translation" drill, which leverages the `syntaxis` backend API to generate sentences from user-provided grammatical templates.

## 2. Goals

*   **Primary:** Provide intermediate Greek learners with a simple, interactive tool to practice specific grammar patterns on demand.
*   **Secondary:** Establish a foundational frontend architecture that can be expanded with more exercise types in the future.
*   **User Experience:** Deliver a clean, intuitive, and focused interface that makes practicing grammar straightforward and efficient.

## 3. User Stories

*   As an intermediate Greek learner, I want to practice specific grammar patterns so that I can solidify my understanding.
*   As a learner, I want to enter a grammatical template and receive an instant exercise based on it.
*   As a learner, I want to see an English sentence and try to translate it into Greek in my head, then click a button to reveal the correct Greek word to check my answer.
*   As a learner, I want to be able to re-do an exercise with the same grammar pattern but a new sentence to get more practice.
*   As a learner, I want a clean and simple interface that lets me focus on the exercises without distractions.

## 4. Functional Requirements

### Main Page
1.  The application must display a main page listing all available exercise types.
2.  For this version, the list shall contain one item: "Translation".
3.  Clicking the "Translation" item shall navigate the user to the translation exercise page.

### Translation Exercise Page
4.  The page must contain a text input field where a user can type or paste a `syntaxis` grammar template.
5.  A "Generate" button must be present next to or below the text input.
6.  Clicking "Generate" must trigger a `POST` request to the `/api/v1/generate` backend endpoint, sending the provided template in the request body.
7.  Upon receiving a successful response, the following content must be displayed, with the words from each line aligned vertically in columns based on the template tokens:
    *   **Line 1:** The original template string provided by the user.
    *   **Line 2:** The generated English sentence.
    *   **Line 3:** The generated Greek sentence.
8.  For the Greek sentence (Line 3), each Greek word must be initially hidden.
9.  Directly below each English word (Line 2), a "Show Answer" button must be displayed.
10. Clicking a "Show Answer" button must toggle the visibility of the corresponding Greek word below it. The button text should change to "Hide Answer" when the word is visible.
11. At the bottom of the exercise display area, two action buttons must be available:
    *   **"Regenerate":** This button will re-submit the current template to the API to fetch a new sentence for a new exercise.
    *   **"Back":** This button will navigate the user back to the main exercise selection page.

### Error Handling
12. If the API call fails due to an invalid template, a user-friendly error message (e.g., "Invalid template provided. Please check the syntax.") must be displayed.
13. If the API call fails for any other reason (e.g., network error, server down), a generic error message (e.g., "Could not connect to the service. Please try again later.") must be displayed.

## 5. Non-Goals (Out of Scope)

*   The application will not include any user accounts or authentication.
*   There will be no scoring, grading, or tracking of user performance.
*   The application will not save a user's history of templates or exercises.
*   The application will not generate or suggest grammar templates for the user.

## 6. Design Considerations

*   **Layout:** A clean, single-column layout for the exercise page is preferred. The template, English sentence, and Greek sentence should be displayed in a grid or using columns to ensure proper alignment of the tokens.
*   **Responsiveness:** The interface should be responsive and usable on both desktop and mobile devices.
*   **Simplicity:** The design should be minimal to keep the focus on the content of the exercise.

## 7. Technical Considerations

*   **Frontend Framework:** **Vue.js** will be used to build the application.
*   **CSS Framework:** **Bootstrap** will be used for styling and layout to ensure a clean, responsive design with minimal custom CSS.
*   **API Communication:** A standard HTTP client like Axios or the native Fetch API should be used for communicating with the backend.
*   **State Management:** For this initial version, component-level state management within Vue will be sufficient.

## 8. Success Metrics

*   A user can successfully complete the full workflow: navigate to the exercise, enter a template, generate a sentence, toggle answers, and use the "Regenerate" or "Back" buttons.
*   The application correctly renders all data received from the `syntaxis` API, including proper alignment of words.
*   The UI is intuitive enough that a first-time user does not need instructions to use the feature.

## 9. Open Questions

*   None at this time. The requirements for this initial version are clear.