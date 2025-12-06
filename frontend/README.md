# YiriAi Frontend

Modern, production-ready React + Tailwind frontend for the YiriAi course selection platform.

## 🎨 Tech Stack

- **Framework**: React 18.2 with Vite 5
- **Styling**: Tailwind CSS 3.3 with custom theme
- **Routing**: React Router 6
- **State Management**: Zustand
- **HTTP Client**: Axios
- **UI Components**: Custom component library with lucide-react icons
- **Animations**: Framer Motion
- **File Upload**: react-dropzone
- **Notifications**: react-hot-toast

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`

### Automated Setup

```bash
cd frontend
./setup-frontend.sh
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Layout.jsx           # Main layout with nav and footer
│   │   └── ui/
│   │       ├── index.jsx        # Base UI components (Button, Input, etc.)
│   │       ├── FormControls.jsx # Advanced form controls (Slider, DayChips, etc.)
│   │       └── Modal.jsx        # Modal and dialog components
│   ├── pages/
│   │   ├── LandingPage.jsx      # Marketing landing page
│   │   ├── SignIn.jsx           # Authentication
│   │   ├── SignUp.jsx           # Registration
│   │   ├── UploadEval.jsx       # Degree eval upload with drag-drop
│   │   ├── Preferences.jsx      # Interactive preference form
│   │   ├── Results.jsx          # Schedule results with PAWS panel
│   │   └── Dashboard.jsx        # Saved schedules management
│   ├── App.jsx                  # Main app with routing
│   ├── main.jsx                 # React entry point
│   └── index.css                # Global styles and Tailwind
├── public/                      # Static assets
├── index.html                   # HTML template
├── vite.config.js              # Vite configuration
├── tailwind.config.js          # Tailwind theme customization
└── package.json                # Dependencies and scripts
```

## 🎯 User Flow

```
Landing Page → Sign Up → Upload Eval → Set Preferences → View Results → Dashboard
                 ↓                                            ↓
              Sign In                                    Copy CRNs to PAWS
```

## 🎨 Design System

### Colors

- **Primary**: Teal (500-900) - Main brand color
- **Accent**: Blue (500-900) - Secondary highlights
- **Success**: Green - Positive actions
- **Warning**: Yellow - Caution states
- **Error**: Red - Errors and destructive actions

### Typography

- **Font**: Inter (Google Fonts)
- **Weights**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

### Components

#### Base Components (`components/ui/index.jsx`)

- **Button**: Primary, secondary, outline, ghost, danger variants
- **Input**: Text input with label and error states
- **Select**: Dropdown with options
- **Checkbox**: Checkbox with label and description
- **Toggle**: Switch component
- **Badge**: Small status indicators
- **Card**: Container with optional hover effect
- **Spinner**: Loading indicator
- **SkeletonLoader**: Placeholder for loading content

#### Form Controls (`components/ui/FormControls.jsx`)

- **Slider**: Range slider with visual feedback
- **DayChips**: Day selection with chips (M, T, W, R, F)
- **TimeRangePicker**: Start/end time selection
- **RadioGroup**: Radio buttons with descriptions
- **ChipGroup**: Multi-select chip interface

#### Modals (`components/ui/Modal.jsx`)

- **Modal**: Base modal with backdrop and animations
- **ConfirmDialog**: Confirmation dialog for destructive actions

### Animations

- **Transitions**: 150-200ms for smooth interactions
- **Fade In**: 300ms fade animation
- **Slide Up/Down**: 300ms slide with opacity
- **Scale In**: 200ms scale with fade
- **Hover Effects**: Cards scale on hover, buttons change color

### Responsive Design

- **Mobile First**: Optimized for mobile screens
- **Breakpoints**:
  - `sm`: 640px
  - `md`: 768px
  - `lg`: 1024px
  - `xl`: 1280px
  - `2xl`: 1536px

## 📄 Pages

### Landing Page

- Hero section with gradient background
- "How It Works" with 3-step visual flow
- Features grid with icons
- Call-to-action sections
- Responsive footer

### Sign In / Sign Up

- Card-based authentication forms
- Input validation
- Password strength indicators (sign up)
- "Remember me" option (sign in)
- Links to switch between forms

### Upload Eval

- Drag-and-drop file upload
- File preview with metadata
- Instructions for getting eval from PAWS
- Parsing progress indicator
- Results display with course list
- Mock data for development (TODO: integrate real API)

### Preferences

- Credit hours slider (min/max)
- Day selection chips (M, T, W, R, F)
- Time range picker (8 AM - 9 PM)
- Campus selection (radio buttons)
- Course modality chips (in-person, hybrid, online)
- Live preference summary
- Form validation

### Results

- **Fit score** badge with percentage
- **Course cards** with:
  - Course code, title, CRN
  - Professor name and RMP rating (star icon)
  - Schedule (days, times, location)
  - Seat availability
  - Modality badge
  - Match reasons (why selected)
- **PAWS Registration Panel** (sticky sidebar):
  - CRN list with copy button
  - Step-by-step PAWS instructions
  - Warning about seat availability
- Actions: Adjust preferences, save schedule

### Dashboard

- Grid of saved schedules
- Each card shows:
  - Schedule name (editable)
  - Creation date
  - Fit score
  - Total credits and course count
  - Course list with CRNs
  - Actions (view, rename, delete)
- Create new schedule button
- Confirmation dialogs for destructive actions

## 🔌 API Integration

### Endpoints (configured via Vite proxy)

All API calls are proxied to `http://localhost:8000`:

- `POST /api/upload-preferences` - Upload eval and preferences
- `GET /api/search-courses` - Search available courses
- `GET /api/professor-rating/{name}` - Get professor ratings
- `GET /health` - Backend health check

### Example Usage

```javascript
import axios from 'axios'

// Upload preferences
const response = await axios.post('/api/upload-preferences', {
  preferences: {
    minCredits: 12,
    maxCredits: 15,
    preferredDays: ['M', 'W', 'F'],
    // ...
  }
})

// Get professor rating
const rating = await axios.get(`/api/professor-rating/${encodeURIComponent(name)}`)
```

## 🧪 Development

### Available Scripts

- `npm run dev` - Start development server (port 5173)
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Environment Variables

Create `.env` file in frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

### Hot Module Replacement (HMR)

Vite provides instant HMR for React components. Changes appear without full page reload.

### Code Style

- Use functional components with hooks
- Keep components under 300 lines
- Extract reusable logic into custom hooks
- Use `clsx` for conditional className logic
- Prefer named exports for components

## 🎯 TODO / Next Steps

### Authentication (Currently Mock)

- [ ] Implement real JWT authentication
- [ ] Add protected routes
- [ ] Store tokens in localStorage/sessionStorage
- [ ] Auto-logout on token expiry

### API Integration

- [ ] Connect upload endpoint to real backend
- [ ] Integrate search with live PAWS data
- [ ] Fetch real RMP ratings
- [ ] Add error handling and retries

### State Management

- [ ] Set up Zustand store for:
  - User authentication
  - Uploaded eval data
  - Preferences
  - Search results
  - Saved schedules
- [ ] Persist state to localStorage

### Features

- [ ] Export schedule to PDF
- [ ] Share schedule link
- [ ] Compare multiple schedules side-by-side
- [ ] Course conflict detection visualization
- [ ] Calendar view of schedule
- [ ] Email reminders for registration

### Performance

- [ ] Code splitting for routes
- [ ] Lazy load heavy components
- [ ] Image optimization
- [ ] Implement service worker for offline support

### Testing

- [ ] Add unit tests (Vitest)
- [ ] Add component tests (React Testing Library)
- [ ] Add E2E tests (Playwright)

### Accessibility

- [x] Semantic HTML
- [x] ARIA labels
- [x] Keyboard navigation
- [x] Focus indicators
- [ ] Screen reader testing
- [ ] WCAG 2.1 AA compliance

## 🚀 Deployment

### Build

```bash
npm run build
```

Output in `dist/` directory.

### Deploy Options

#### Static Hosting (Vercel, Netlify)

```bash
# Vercel
npm i -g vercel
vercel --prod

# Netlify
npm i -g netlify-cli
netlify deploy --prod
```

#### Docker

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### nginx Configuration

```nginx
server {
    listen 80;
    server_name yiriai.com;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🐛 Troubleshooting

### Port already in use

```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

### Dependencies not installing

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Tailwind styles not applying

```bash
# Rebuild Tailwind
npm run build:css
# Or restart dev server
npm run dev
```

### API calls failing

1. Check backend is running: `curl http://localhost:8000/health`
2. Check Vite proxy config in `vite.config.js`
3. Check browser console for CORS errors

## 📚 Resources

- [React Docs](https://react.dev)
- [Vite Guide](https://vitejs.dev/guide/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [React Router](https://reactrouter.com)
- [Lucide Icons](https://lucide.dev)
- [Framer Motion](https://www.framer.com/motion/)

## 📝 License

Part of the YiriAi project. Educational use only.
