import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'dark',  // Enable dark mode
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
    background: {
      default: '#121212',
      paper: '#333333',
    },
  },
  typography: {
    fontFamily:"'Palatino', sans-serif",
    allVariants: {
      color: '#ffffff'
    }
  },
});

export default theme;