from supabase_client import supabase_service

class AuthService:

    def sign_up(self, full_name, email, password):
        """
        Sign up a new user
        
        Args:
            full_name: User's full name
            email: User email
            password: User password
            
        Returns:
            (user, error) - tuple with user data or error message
        """
        try:
            # 1. Create auth user with Supabase
            response = supabase_service.sign_up(email, password)

            if response.user is None:
                return None, "Signup failed - please check your email and password"

            user_id = response.user.id

            # 2. Save profile to database
            try:
                profile_response = supabase_service.client.table("profiles").insert({
                    "id": user_id,
                    "full_name": full_name,
                    "email": email
                }).execute()
                
                print(f"✓ Profile created for user: {email}")
            except Exception as profile_error:
                print(f"⚠️  User created but profile save failed: {profile_error}")
                # Still return success because auth user was created
                # Profile can be created later
                return response.user, None

            return response.user, None
            
        except Exception as e:
            print(f"❌ Signup error: {e}")
            error_msg = str(e)
            # Extract user-friendly error messages
            if "already registered" in error_msg:
                return None, "This email is already registered"
            elif "password" in error_msg.lower():
                return None, "Password must be at least 6 characters"
            else:
                return None, f"Signup failed: {error_msg}"

    def login(self, email, password):
        """
        Log in a user
        
        Args:
            email: User email
            password: User password
            
        Returns:
            (session, error) - tuple with session data or error message
        """
        try:
            response = supabase_service.sign_in(email, password)

            if response.user is None:
                return None, "Invalid email or password"

            print(f"✓ User logged in: {email}")
            return response, None
            
        except Exception as e:
            print(f"❌ Login error: {e}")
            error_msg = str(e)
            if "Invalid login credentials" in error_msg:
                return None, "Invalid email or password"
            else:
                return None, f"Login failed: {error_msg}"


auth_service = AuthService()