<template>
  <v-container fluid class="fill-height auth-background">
    <v-row justify="center" align="center" class="fill-height">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="elevation-12 rounded-xl">
          <v-card-title class="text-center pa-6 bg-primary">
            <v-icon icon="mdi-shield-check" size="48" class="mb-2" />
            <h1 class="text-h4 font-weight-bold">Insurance Claims</h1>
            <p class="text-body-2 mt-2 opacity-80">
              Secure Claims Management System
            </p>
          </v-card-title>

          <v-tabs v-model="tab" grow color="primary">
            <v-tab value="login">
              <v-icon start icon="mdi-login" />
              Login
            </v-tab>
            <v-tab value="register">
              <v-icon start icon="mdi-account-plus" />
              Register
            </v-tab>
          </v-tabs>

          <v-card-text class="pa-6">
            <v-tabs-window v-model="tab">
              <!-- Login Form -->
              <v-tabs-window-item value="login">
                <v-form ref="loginFormRef" @submit.prevent="handleLogin">
                  <v-text-field
                    v-model="loginForm.email"
                    label="Email"
                    type="email"
                    variant="outlined"
                    prepend-inner-icon="mdi-email"
                    :rules="[rules.required, rules.email]"
                    :disabled="loading"
                    class="mb-4"
                  />

                  <v-text-field
                    v-model="loginForm.password"
                    label="Password"
                    :type="showPassword ? 'text' : 'password'"
                    variant="outlined"
                    prepend-inner-icon="mdi-lock"
                    :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                    :rules="[rules.required, rules.minLength(8)]"
                    :disabled="loading"
                    @click:append-inner="showPassword = !showPassword"
                  />

                  <v-btn
                    type="submit"
                    color="primary"
                    size="large"
                    block
                    class="mt-4"
                    :loading="loading"
                  >
                    <v-icon start icon="mdi-login" />
                    Sign In
                  </v-btn>
                </v-form>
              </v-tabs-window-item>

              <!-- Register Form -->
              <v-tabs-window-item value="register">
                <v-form ref="registerFormRef" @submit.prevent="handleRegister">
                  <v-text-field
                    v-model="registerForm.username"
                    label="Username"
                    variant="outlined"
                    prepend-inner-icon="mdi-account"
                    :rules="[rules.required, rules.minLength(3)]"
                    :disabled="loading"
                    class="mb-4"
                  />

                  <v-text-field
                    v-model="registerForm.email"
                    label="Email"
                    type="email"
                    variant="outlined"
                    prepend-inner-icon="mdi-email"
                    :rules="[rules.required, rules.email]"
                    :disabled="loading"
                    class="mb-4"
                  />

                  <v-text-field
                    v-model="registerForm.password"
                    label="Password"
                    :type="showPassword ? 'text' : 'password'"
                    variant="outlined"
                    prepend-inner-icon="mdi-lock"
                    :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                    :rules="[rules.required, rules.minLength(8)]"
                    :disabled="loading"
                    @click:append-inner="showPassword = !showPassword"
                  />

                  <v-btn
                    type="submit"
                    color="primary"
                    size="large"
                    block
                    class="mt-4"
                    :loading="loading"
                  >
                    <v-icon start icon="mdi-account-plus" />
                    Create Account
                  </v-btn>
                </v-form>
              </v-tabs-window-item>
            </v-tabs-window>
          </v-card-text>
        </v-card>

        <!-- Snackbar for messages -->
        <v-snackbar
          v-model="snackbar.show"
          :color="snackbar.color"
          :timeout="3000"
        >
          {{ snackbar.message }}
          <template #actions>
            <v-btn variant="text" @click="snackbar.show = false">
              Close
            </v-btn>
          </template>
        </v-snackbar>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import type { LoginInput, RegisterInput } from "~/shared/types";

definePageMeta({
  layout: false,
});

const { login, register, currentUser, userRole } = useAuth();
const router = useRouter();

const tab = ref("login");
const loading = ref(false);
const showPassword = ref(false);
const loginFormRef = ref();
const registerFormRef = ref();

const loginForm = reactive<LoginInput>({
  email: "",
  password: "",
});

const registerForm = reactive<RegisterInput>({
  username: "",
  email: "",
  password: "",
});

const snackbar = reactive({
  show: false,
  message: "",
  color: "success",
});

const rules = {
  required: (v: string) => !!v || "This field is required",
  email: (v: string) => /.+@.+\..+/.test(v) || "Invalid email address",
  minLength: (min: number) => (v: string) =>
    v.length >= min || `Must be at least ${min} characters`,
};

const showMessage = (message: string, color: string = "success") => {
  snackbar.message = message;
  snackbar.color = color;
  snackbar.show = true;
};

const redirectBasedOnRole = (role: string) => {
  switch (role) {
    case "VERIFIER":
      router.push("/verifier");
      break;
    case "APPROVER":
      router.push("/approver");
      break;
    default:
      router.push("/user");
  }
};

const handleLogin = async () => {
  const { valid } = await loginFormRef.value?.validate();
  if (!valid) return;

  loading.value = true;
  try {
    await login(loginForm);
    showMessage("Login successful!");
    
    // Wait for user data to be loaded
    await nextTick();
    
    if (userRole.value) {
      redirectBasedOnRole(userRole.value);
    }
  } catch (error: any) {
    const message = error.response?.data?.detail || "Invalid credentials";
    showMessage(message, "error");
  } finally {
    loading.value = false;
  }
};

const handleRegister = async () => {
  const { valid } = await registerFormRef.value?.validate();
  if (!valid) return;

  loading.value = true;
  try {
    await register(registerForm);
    showMessage("Registration successful! Please login.");
    tab.value = "login";
    loginForm.email = registerForm.email;
    loginForm.password = "";
    registerForm.username = "";
    registerForm.email = "";
    registerForm.password = "";
  } catch (error: any) {
    const message =
      error.response?.data?.detail || "Registration failed. Please try again.";
    showMessage(message, "error");
  } finally {
    loading.value = false;
  }
};

// Redirect if already authenticated
onMounted(() => {
  if (currentUser.value && userRole.value) {
    redirectBasedOnRole(userRole.value);
  }
});

// Watch for auth changes
watch(currentUser, (user) => {
  if (user) {
    redirectBasedOnRole(user.role);
  }
});
</script>

<style scoped>
.auth-background {
  background: linear-gradient(135deg, #1976d2 0%, #0d47a1 100%);
  min-height: 100vh;
}
</style>
