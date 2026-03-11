import "@mdi/font/css/materialdesignicons.css";

import "vuetify/styles";
import { createVuetify } from "vuetify";

export default defineNuxtPlugin((app) => {
  const vuetify = createVuetify({
    theme: {
      defaultTheme: "dark",
      themes: {
        light: {
          dark: false,
          colors: {
            primary: "#1976D2",
            secondary: "#424242",
            accent: "#82B1FF",
            error: "#FF5252",
            info: "#2196F3",
            success: "#4CAF50",
            warning: "#FFC107",
            background: "#F5F5F5",
            surface: "#FFFFFF",
          },
        },
        dark: {
          dark: true,
          colors: {
            primary: "#2196F3",
            secondary: "#424242",
            accent: "#FF4081",
            error: "#FF5252",
            info: "#2196F3",
            success: "#4CAF50",
            warning: "#FFC107",
            background: "#121212",
            surface: "#1E1E1E",
          },
        },
      },
    },
    defaults: {
      VBtn: {
        rounded: "lg",
      },
      VCard: {
        rounded: "lg",
      },
      VTextField: {
        variant: "outlined",
        density: "comfortable",
      },
      VTextarea: {
        variant: "outlined",
        density: "comfortable",
      },
      VSelect: {
        variant: "outlined",
        density: "comfortable",
      },
    },
  });
  app.vueApp.use(vuetify);
});
