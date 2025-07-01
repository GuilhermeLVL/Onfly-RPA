import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  TextField,
  Button,
  Box,
  Paper,
  CircularProgress,
  CssBaseline,
  createTheme,
  ThemeProvider,
  List,
  ListItem,
  Tabs,
  Tab
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { DataGrid } from '@mui/x-data-grid';

const theme = createTheme({
  palette: {
    mode: 'dark', // Enable dark mode
    primary: {
      main: '#3F51B5', // Deep blue, inspired by dark/water Pokémon
    },
    secondary: {
      main: '#FFC107', // Vibrant yellow, inspired by electric/fire Pokémon
    },
    background: {
      default: '#121212', // Very dark grey
      paper: '#1E1E1E', // Slightly lighter dark grey for cards/papers
    },
    text: {
      primary: '#FFFFFF', // White text for readability on dark backgrounds
      secondary: '#B0B0B0', // Lighter grey for secondary text
    },
  },
});

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function CustomTabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`,
  };
}

interface ChatMessage {
  sender: 'user' | 'ai';
  text: string;
}

function App() {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [pipelineReport, setPipelineReport] = useState<any[]>([]);
  const [pipelineChartUrl, setPipelineChartUrl] = useState<string | null>(null);
  const [chatData, setChatData] = useState<any[]>([]);
  const [tabValue, setTabValue] = useState(0);

  const API_BASE_URL = 'http://localhost:8001';

  const fetchChatHistory = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/get_chat_history`);
      const data = await response.json();
      if (data.history) {
        const parsedHistory: ChatMessage[] = data.history.split('\n')
          .filter((line: string) => line.trim() !== '')
          .map((line: string) => {
            if (line.startsWith('Você:')) {
              return { sender: 'user', text: line.substring('Você:'.length).trim() };
            } else if (line.startsWith('IA:')) {
              return { sender: 'ai', text: line.substring('IA:'.length).trim() };
            }
            return { sender: 'ai', text: line.trim() }; // Fallback for old or malformed messages
          });
        setChatHistory(parsedHistory);
      }
    } catch (error) {
      console.error('Erro ao buscar histórico do chat:', error);
    }
  };

  const fetchPipelineReport = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/get_pipeline_report`);
      const data = await response.json();
      setPipelineReport(data);
    } catch (error) {
      console.error('Erro ao buscar relatório do pipeline:', error);
    }
  };

  const fetchPipelineChart = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/get_pipeline_chart`);
      if (response.ok) {
        const blob = await response.blob();
        setPipelineChartUrl(URL.createObjectURL(blob));
      } else {
        console.error('Erro ao buscar gráfico do pipeline:', response.statusText);
        setPipelineChartUrl(null);
      }
    } catch (error) {
      console.error('Erro ao buscar gráfico do pipeline:', error);
      setPipelineChartUrl(null);
    }
  };

  const fetchChatData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/get_chat_data`);
      const data = await response.json();
      setChatData(data.data);
    } catch (error) {
      console.error('Erro ao buscar dados do chat:', error);
    }
  };

  useEffect(() => {
    fetchChatHistory();
    fetchPipelineReport();
    fetchPipelineChart();
    fetchChatData();
  }, []);

  const handleSendMessage = async () => {
    if (!message.trim()) return;

    setLoading(true);
    // Add user message to history immediately
    setChatHistory((prev) => [...prev, { sender: 'user', text: message }]);
    setMessage('');

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pergunta: message }),
      });

      if (response.ok) {
        const data = await response.json();
        // Assuming the API returns the AI's response directly
        if (data.resposta) {
          setChatHistory((prev) => [...prev, { sender: 'ai', text: data.resposta }]);
        }
        await fetchChatData(); // Update chat data
      } else {
        const errorData = await response.json();
        setChatHistory((prev) => [...prev, { sender: 'ai', text: `Erro: ${errorData.detail || 'Ocorreu um erro.'}` }]);
      }
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      setChatHistory((prev) => [...prev, { sender: 'ai', text: `Erro de conexão: ${error}` }]);
    } finally {
      setLoading(false);
    }
  };

  const handleRunPipeline = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/run_pipeline`, {
        method: 'POST',
      });
      const data = await response.json();
      alert(data.message);
      await fetchPipelineReport();
      await fetchPipelineChart();
    } catch (error) {
      console.error('Erro ao executar pipeline:', error);
      alert('Erro ao executar pipeline.');
    }
    finally {
      setLoading(false);
    }
  };

  const handleClearContext = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/clear_context`, {
        method: 'POST',
      });
      const data = await response.json();
      alert(data.message);
      setChatHistory([]);
      setChatData([]);
    } catch (error) {
      console.error('Erro ao limpar contexto:', error);
      alert('Erro ao limpar contexto.');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Pokémon RPA Chatbot
          </Typography>
          <Button color="inherit" onClick={handleRunPipeline} disabled={loading}>
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Executar Pipeline'}
          </Button>
          <Button color="inherit" onClick={handleClearContext} disabled={loading} sx={{ ml: 2 }}>
            Limpar Contexto
          </Button>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="basic tabs example">
            <Tab label="Chat" {...a11yProps(0)} />
            <Tab label="Dados do Pipeline" {...a11yProps(1)} />
            <Tab label="Dados do Chat" {...a11yProps(2)} />
          </Tabs>
        </Box>
        <CustomTabPanel value={tabValue} index={0}>
          <Paper elevation={3} sx={{ p: 2, height: '60vh', overflowY: 'auto', mb: 2, display: 'flex', flexDirection: 'column' }}>
            <List sx={{ flexGrow: 1, p: 0 }}>
              {chatHistory.map((chatMessage, index) => (
                <ListItem
                  key={index}
                  sx={{
                    justifyContent: chatMessage.sender === 'user' ? 'flex-end' : 'flex-start',
                    padding: '8px 0',
                    mb: 1, // Add margin-bottom for spacing between messages
                  }}
                >
                  <Box
                    sx={{
                      maxWidth: '70%',
                      padding: '10px 15px',
                      borderRadius: '20px',
                      bgcolor: chatMessage.sender === 'user' ? theme.palette.primary.main : theme.palette.background.paper, // Use primary.main for user, background.paper for AI
                      color: chatMessage.sender === 'user' ? 'white' : theme.palette.text.primary,
                      display: 'flex',
                      flexDirection: 'column',
                      wordBreak: 'break-word',
                    }}
                  >
                    <Typography
                      variant="caption"
                      sx={{
                        fontWeight: 'bold',
                        mb: 0.5,
                        color: chatMessage.sender === 'user' ? 'rgba(255,255,255,0.7)' : theme.palette.text.secondary,
                      }}
                    >
                      {chatMessage.sender === 'user' ? 'Você:' : 'IA:'}
                    </Typography>
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                      {chatMessage.text}
                    </Typography>
                  </Box>
                </ListItem>
              ))}
            </List>
            {loading && <CircularProgress size={24} sx={{ display: 'block', mx: 'auto', mt: 2 }} />}
          </Paper>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Digite sua mensagem..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleSendMessage();
                }
              }}
              disabled={loading}
            />
            <Button
              variant="contained"
              endIcon={<SendIcon />}
              onClick={handleSendMessage}
              disabled={loading}
            >
              Enviar
            </Button>
          </Box>
        </CustomTabPanel>
        <CustomTabPanel value={tabValue} index={1}>
          <Typography variant="h5" gutterBottom>Relatório do Pipeline</Typography>
          {pipelineReport.length > 0 ? (
            <Box sx={{ height: 400, width: '100%' }}>
              <DataGrid
                rows={pipelineReport}
                columns={Object.keys(pipelineReport[0]).map(key => ({ field: key, headerName: key, width: 150 }))}
                pageSizeOptions={[5, 10, 20]}
                checkboxSelection
                disableRowSelectionOnClick
              />
            </Box>
          ) : (
            <Typography>Nenhum relatório disponível. Execute o pipeline.</Typography>
          )}

          <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>Gráfico do Pipeline</Typography>
          {pipelineChartUrl ? (
            <Box sx={{ mt: 2, textAlign: 'center' }}>
              <img src={pipelineChartUrl} alt="Gráfico do Pipeline" style={{ maxWidth: '100%', height: 'auto' }} />
            </Box>
          ) : (
            <Typography>Nenhum gráfico disponível. Execute o pipeline.</Typography>
          )}
        </CustomTabPanel>
        <CustomTabPanel value={tabValue} index={2}>
          <Typography variant="h5" gutterBottom>Dados Gerados pelo Chat</Typography>
          {chatData.length > 0 ? (
            <List>
              {chatData.map((item, index) => (
                <Paper key={index} elevation={2} sx={{ p: 2, mb: 2}}>
                  <Typography variant="h6">Arquivo: {item.filename} ({item.type})</Typography>
                  {item.type === 'csv' && item.content.length > 0 && (
                    <Box sx={{ height: 200, width: '100%', mt: 1 }}>
                      <DataGrid
                        rows={item.content}
                        columns={Object.keys(item.content[0]).map(key => ({ field: key, headerName: key, width: 150 }))}
                        pageSizeOptions={[5, 10]}
                        disableRowSelectionOnClick
                      />
                    </Box>
                  )}
                  {item.type === 'json' && (
                    <Box sx={{ mt: 1, bgcolor: 'grey.100', p: 1, borderRadius: 1, overflowX: 'auto' }}>
                      <pre>{JSON.stringify(item.content, null, 2)}</pre>
                    </Box>
                  )}
                </Paper>
              ))}
            </List>
          ) : (
            <Typography>Nenhum dado gerado pelo chat disponível.</Typography>
          )}
        </CustomTabPanel>
      </Container>
    </ThemeProvider>
  );
}

export default App;
