// src/pages/VerifyEmailPage.tsx
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

function VerifyEmailPage() {
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [email, setEmail] = useState("");
  const [searchParams] = useSearchParams();

  useEffect(() => { 
    // Extract email from query params
    const emailParam = searchParams.get("email");
    if (emailParam) {
      setEmail(emailParam);
      // Implement verification logic here
      setStatus("success");
    }
  }, [searchParams]);

  return (
    <div className="flex min-h-svh flex-col items-center justify-center p-4">
      <div className="text-center">
        {status === "loading" && <p>Verifying email...</p>}
        {status === "success" && (
          <div>
            <p>Verification email sent to {email}</p>
            <p>Please check your inbox and click the verification link.</p>
          </div>
        )}
        {status === "error" && <p>Verification failed. Please try again.</p>}
      </div>
    </div>
  );
}

export default VerifyEmailPage;