# HistoryPage - Essay History Management

## Overview
The HistoryPage component provides a comprehensive interface for viewing, managing, and filtering previously graded essays. It integrates with Supabase backend to display real-time essay scoring data.

## Features

### 📊 Core Functionality
- **Real-time Data Display**: Fetches essay history from Supabase database
- **Advanced Filtering**: Filter by essay type, date, and search functionality
- **Sorting Options**: Sort by date, score, student name, or status
- **Bulk Operations**: Select multiple essays for bulk actions
- **Individual Essay Management**: View details, update status, add teacher notes

### 🔍 Filtering System
- **Essay Type Filter**: 
  - All Types
  - Argumentative Essay
  - Expository Essay
  - Narrative Essay
  - Research Paper
- **Date Filter**: Filter by specific submission date
- **Search**: Search by essay title or student name
- **Clear Filters**: Reset all filters with one click

### 📝 Essay Management
- **Status Management**: 
  - Graded
  - For Review
  - Returned
- **Teacher Notes**: Add private notes for each essay
- **Essay Details**: View complete rubric breakdown and scores
- **Delete Essays**: Remove individual or bulk essays

## Technical Implementation

### Frontend Components
- **React Hooks**: `useState`, `useEffect`, `useMemo` for state management
- **API Integration**: Fetches data from `/api/essay-history` endpoint
- **Real-time Updates**: Automatic data refresh and state synchronization

### Backend Integration
- **Supabase Client**: Database operations for essay storage
- **REST API Endpoints**: 
  - `GET /api/essay-history` - Fetch all essays
  - `PUT /api/essay-history/:id` - Update essay status/notes
  - `DELETE /api/essay-history/:id` - Delete essay

### Data Structure
```javascript
{
  id: number,
  title: string,
  student: string,
  type: string,
  date: string,
  totalScore: number,
  maxScore: number,
  status: string,
  notes: string,
  criteria: Array<{
    name: string,
    score: number,
    max: number
  }>
}
```

## File Structure

### Frontend
```
frontend/src/assets/pages/
├── HistoryPage.jsx          # Main component
└── HistoryPage.css          # Styling (if exists)
```

### Backend
```
backend/
├── app.py                   # API endpoints
├── supabase_client.py       # Database operations
└── scoring_service.py        # Essay scoring logic
```

## API Endpoints

### GET /api/essay-history
**Response:**
```json
{
  "success": true,
  "essays": [
    {
      "id": 1,
      "title": "Essay Title",
      "student": "Student Name",
      "type": "Argumentative Essay",
      "date": "2026-04-23",
      "totalScore": 85,
      "maxScore": 100,
      "status": "Graded",
      "notes": "",
      "criteria": [
        {"name": "Thesis", "score": 22, "max": 25},
        {"name": "Evidence", "score": 20, "max": 25}
      ]
    }
  ]
}
```

### PUT /api/essay-history/:id
**Request Body:**
```json
{
  "status": "Graded",
  "notes": "Excellent work on thesis statement"
}
```

### DELETE /api/essay-history/:id
**Response:**
```json
{
  "success": true,
  "message": "Essay deleted successfully"
}
```

## Integration with Essay Scoring

### Automatic Essay Saving
When an essay is scored via the ScorerPage:
1. Essay is automatically saved to Supabase
2. Essay type is determined by selected rubric
3. Score breakdown is stored with criteria details
4. Essay appears immediately in HistoryPage

### Essay Type Mapping
- **Rubric ID 1** → "Argumentative Essay"
- **Rubric ID 2** → "Expository Essay"
- **Rubric ID 3** → "Narrative Essay"
- **Rubric ID 4** → "Research Paper"

## UI Components

### Filter Bar
- Search input for essay titles/students
- Essay type dropdown selector
- Date picker for specific dates
- Clear filters button

### Essay Table
- Checkbox for bulk selection
- Essay title and student name
- Essay type badge
- Submission date
- Score display with color coding
- Status dropdown
- Action buttons (View, Edit, Delete)

### Modal Windows
- **View Essay Modal**: Display complete essay details and rubric breakdown
- **Notes Modal**: Add/edit teacher notes
- **Confirmation Modals**: Delete confirmations

## State Management

### React State
```javascript
const [essays, setEssays] = useState([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);
const [filterType, setFilterType] = useState('All Types');
const [filterDate, setFilterDate] = useState('');
const [search, setSearch] = useState('');
const [selected, setSelected] = useState([]);
```

### Data Flow
1. Component mounts → `useEffect` triggers
2. API call to `/api/essay-history`
3. Data fetched from Supabase
4. Essays state updated
5. Filters applied using `useMemo`
6. UI renders filtered results

## Error Handling

### Frontend Errors
- Network connectivity issues
- API response errors
- Loading states
- Empty state handling

### Backend Errors
- Supabase connection failures
- Database query errors
- Invalid essay IDs
- Permission issues

## Performance Optimizations

### Frontend
- `useMemo` for expensive filtering operations
- Debounced search input
- Efficient state updates
- Component memoization where needed

### Backend
- Database query optimization
- Efficient data serialization
- Proper error handling
- Connection pooling

## Styling and UX

### Visual Design
- Clean, modern interface
- Color-coded score ranges
- Responsive design
- Loading animations
- Hover states and transitions

### Accessibility
- Semantic HTML structure
- Keyboard navigation support
- Screen reader compatibility
- High contrast support

## Testing

### Frontend Tests
- Component rendering
- Filter functionality
- API integration
- User interactions

### Backend Tests
- API endpoint responses
- Database operations
- Error handling
- Data validation

## Deployment Considerations

### Environment Variables
```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Database Setup
- Supabase project configuration
- Table schema setup
- Row Level Security (RLS) policies
- Index optimization

## Future Enhancements

### Planned Features
- Export functionality (PDF, CSV)
- Advanced analytics dashboard
- Email notifications
- Bulk grading operations
- Essay comparison tools

### Performance Improvements
- Pagination for large datasets
- Caching strategies
- Real-time updates via WebSockets
- Lazy loading

## Troubleshooting

### Common Issues
1. **Essays not appearing**: Check Supabase connection and API endpoints
2. **Filtering not working**: Verify data structure matches expected format
3. **Status updates failing**: Check API permissions and database schema
4. **Performance issues**: Consider pagination and query optimization

### Debug Steps
1. Check browser console for errors
2. Verify API responses in Network tab
3. Check Supabase database directly
4. Review backend logs for errors

## Contributing

### Code Style
- Follow React best practices
- Use semantic naming conventions
- Implement proper error handling
- Add appropriate comments

### Pull Request Guidelines
- Test all functionality
- Update documentation
- Follow existing code patterns
- Include screenshots for UI changes

---

## Quick Start Guide

1. **Setup Supabase**: Configure database and get API keys
2. **Environment Variables**: Add `.env` file with credentials
3. **Install Dependencies**: Run `npm install` in frontend
4. **Start Backend**: `python app.py` in backend directory
5. **Start Frontend**: `npm run dev` in frontend directory
6. **Access**: Navigate to `http://localhost:5173`

---

**Last Updated**: April 23, 2026
**Version**: 1.0.0
**Author**: Machine Learning Essay Scoring System
