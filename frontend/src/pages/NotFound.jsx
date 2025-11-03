import { useNavigate } from "react-router-dom";

function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="error-container">
      <div className="error-card">
        {/* Warning icon in red */}
        <svg 
          width="120" 
          height="120" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          style={{color: '#EF4444', marginBottom: '2rem'}}
        >
          <circle cx="12" cy="12" r="10" strokeWidth="1.5"/>
          <line x1="15" y1="9" x2="9" y2="15" strokeWidth="1.5" strokeLinecap="round"/>
          <line x1="9" y1="9" x2="15" y2="15" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>

        {/* Large 404 text */}
        <h1 style={{
          fontSize: '4rem',
          fontWeight: '800',
          color: '#EF4444',
          marginBottom: '1rem',
          lineHeight: 1
        }}>
          404
        </h1>

        {/* Page not found text */}
        <h2 style={{
          fontSize: '1.5rem',
          fontWeight: '700',
          color: '#1F2937',
          marginBottom: '0.5rem'
        }}>
          Page Not Found
        </h2>

        <p style={{
          fontSize: '1rem',
          color: '#6B7280',
          marginBottom: '2rem',
          maxWidth: '400px'
        }}>
          The page you're looking for doesn't exist or has been moved. 
          Please check the URL or return to the homepage.
        </p>

        {/* Navigation buttons: Home and Back */}
        <div style={{
          display: 'flex',
          gap: '1rem',
          flexWrap: 'wrap',
          justifyContent: 'center',
          marginBottom: '2rem'
        }}>
          <button 
            onClick={() => navigate("/")} 
            className="cta-button"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <span>Go Home</span>
          </button>

          <button 
            onClick={() => navigate(-1)} 
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              background: 'white',
              border: '2px solid #E5E7EB',
              color: '#374151',
              padding: '1rem 2rem',
              borderRadius: '9999px',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s ease'
            }}
            onMouseOver={(e) => {
              e.target.style.background = '#F9FAFB';
              e.target.style.borderColor = '#D1D5DB';
            }}
            onMouseOut={(e) => {
              e.target.style.background = 'white';
              e.target.style.borderColor = '#E5E7EB';
            }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M19 12H5M12 19l-7-7 7-7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <span>Go Back</span>
          </button>
        </div>

        {/* Helpful navigation links */}
        <div style={{
          marginTop: '2rem',
          paddingTop: '2rem',
          borderTop: '1px solid #E5E7EB'
        }}>
          <p style={{
            fontSize: '0.875rem',
            color: '#6B7280',
            marginBottom: '1rem'
          }}>
            Need help? Try these:
          </p>
          <div style={{
            display: 'flex',
            gap: '1rem',
            justifyContent: 'center',
            flexWrap: 'wrap'
          }}>
            <button 
              onClick={() => navigate("/patient-info")}
              style={{
                background: 'none',
                border: 'none',
                color: '#0EA5E9',
                fontSize: '0.875rem',
                fontWeight: '600',
                cursor: 'pointer',
                textDecoration: 'underline'
              }}
            >
              Start Diagnosis
            </button>
            <span style={{color: '#D1D5DB'}}>•</span>
            <button 
              onClick={() => navigate("/chat")}
              style={{
                background: 'none',
                border: 'none',
                color: '#0EA5E9',
                fontSize: '0.875rem',
                fontWeight: '600',
                cursor: 'pointer',
                textDecoration: 'underline'
              }}
            >
              Chat
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default NotFound;
