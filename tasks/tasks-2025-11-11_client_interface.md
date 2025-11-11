## Relevant Files

- `client/src/main.js` - Main entry point for the Vue app, where Vue, Vue Router, and Bootstrap are initialized.
- `client/src/router/index.js` - Configuration file for all application routes (e.g., `/` and `/exercise/translation`).
- `client/src/App.vue` - The root application component that contains the `<router-view>` to render different pages.
- `client/src/services/api.js` - A dedicated service file to handle all communication with the `syntaxis` backend API.
- `client/src/views/HomeView.vue` - The main landing page component that will display the list of available exercises.
- `client/src/views/TranslationExerciseView.vue` - The component for the translation exercise page, managing state for the template input and API data.
- `client/src/components/ExerciseDisplay.vue` - A reusable component responsible for rendering the aligned template, English sentence, and Greek sentence.
- `client/src/components/Word.vue` - A small, reusable component to display a single English word and its corresponding togglable Greek answer.
- `client/tests/unit/` - Directory for all unit tests. Corresponding test files like `HomeView.spec.js`, `TranslationExerciseView.spec.js`, etc., will be created here.

### Notes

- Unit tests should be created for each component to ensure its functionality is correct.
- Use the Vue Test Utils library for component testing.
- To run tests, you can typically use the command `npm test` or `npm run test:unit` from within the `client` directory, depending on the Vue project setup.

## Tasks

- [x] 1.0 Set up the Vue.js project structure
  - [x] 1.1 Initialize a new Vue.js project in a `client/` directory using `create-vue` (`npm create vue@latest`).
  - [x] 1.2 Add Vue Router during the project setup prompts.
  - [x] 1.3 Install Bootstrap and its dependencies (`npm install bootstrap`).
  - [x] 1.4 Install Axios for API communication (`npm install axios`).
  - [x] 1.5 Import Bootstrap's CSS in the main entry file (`client/src/main.js`).
  - [x] 1.6 Create the proposed directory structure: `client/src/views`, `client/src/components`, `client/src/services`.

- [x] 2.0 Implement application routing and main page layout
  - [x] 2.1 Create the `HomeView.vue` and `TranslationExerciseView.vue` files inside the `client/src/views` directory.
  - [x] 2.2 Configure the Vue Router in `client/src/router/index.js` to define two routes:
    - `{ path: '/', name: 'home', component: HomeView }`
    - `{ path: '/exercise/translation', name: 'translation', component: TranslationExerciseView }`
  - [x] 2.3 Update `App.vue` to include a basic layout with a header and the `<router-view>` element.
  - [x] 2.4 In `HomeView.vue`, implement the UI to show a list containing a single item, "Translation," which links to the `/exercise/translation` route.

- [x] 3.0 Develop the Translation Exercise page UI
  - [x] 3.1 In `TranslationExerciseView.vue`, add a `<textarea>` for the user to input the grammar template and a "Generate" `<button>`.
  - [x] 3.2 Create the `ExerciseDisplay.vue` component file in `client/src/components`. This component should accept `template` (string) and `lexicals` (array of objects) as props.
  - [x] 3.3 Inside `ExerciseDisplay.vue`, use Bootstrap's grid system (`row`, `col`) to render the three lines of text in aligned columns.
  - [x] 3.4 Create the `Word.vue` component file. It should accept `englishWord` and `greekWord` as props.
  - [x] 3.5 In `Word.vue`, display the `englishWord` and a "Show Answer" button.
  - [x] 3.6 Add the "Regenerate" and "Back" buttons at the bottom of the `TranslationExerciseView.vue` template.

- [x] 4.0 Integrate with the `syntaxis` backend API
  - [x] 4.1 Create the `api.js` file in `client/src/services`.
  - [x] 4.2 In `api.js`, create a function `generateSentence(template)` that performs a `POST` request to `/api/v1/generate` using Axios.
  - [x] 4.3 The function should send the `template` string in the request body.
  - [x] 4.4 Implement error handling within the service to catch API errors and return a consistent error format.

- [ ] 5.0 Implement the core exercise logic and user interactions
  - [ ] 5.1 In `TranslationExerciseView.vue`, import and use the `generateSentence` service. When the "Generate" button is clicked, call this service with the content of the text area.
  - [ ] 5.2 Store the API response data in the component's state and pass it as props to the `ExerciseDisplay` component.
  - [ ] 5.3 In the `Word.vue` component, implement the local state and logic to toggle the visibility of the `greekWord` when the "Show Answer" / "Hide Answer" button is clicked.
  - [ ] 5.4 In `TranslationExerciseView.vue`, wire up the "Regenerate" button to call the `generateSentence` service again with the current template.
  - [ ] 5.5 Wire up the "Back" button to navigate to the home route (`/`) using Vue Router's programmatic navigation.
  - [ ] 5.6 Add a data property to `TranslationExerciseView.vue` to hold error messages, and display them in the template if an API call fails.
