// https://nuxt.com/docs/api/configuration/nuxt-config
import vuetify, { transformAssetUrls } from "vite-plugin-vuetify";
import { resolve } from "pathe";
export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },

  build: {
    transpile: ["vuetify"],
  },

  runtimeConfig: {
    apiBaseUrl: "http://localhost:8000",
    public: {
      apiBaseUrl: "/api",
    },
  },

  vite: {
    plugins: [
      // @ts-expect-error
      vuetify({ autoImport: true }),
    ],
    vue: {
      template: {
        transformAssetUrls,
      },
    },
  },

  modules: [
    "@nuxt/a11y",
    "@nuxt/eslint",
    "@nuxt/image",
    "@nuxt/test-utils",
    "@artmizu/nuxt-prometheus",
    "@pinia/nuxt",
  ],

  alias: {
    $types: resolve(__dirname, "types"),
    $components: resolve(__dirname, "app/components"),
    $utils: resolve(__dirname, "utils"),
    $libs: resolve(__dirname, "libs"),
    $assets: resolve(__dirname, "assets"),
    $constants: resolve(__dirname, "constants"),
    $shared: resolve(__dirname, "shared"),
  },
});
