import { StrictMode, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { ArrowUpRight, BriefcaseBusiness, FileText, LoaderCircle, Sparkles } from 'lucide-react';
import './styles.css';

const sampleResume = 'Product analyst with 3 years of experience building SQL dashboards and Python forecasting models. Led a customer retention project that improved activation by 18%. Partnered with design and engineering in agile teams.';
const sampleJob = 'We are looking for a product analyst who can use SQL and Python to turn customer data into decisions. You will partner with engineering and design, own experiments, and communicate insights to stakeholders.';

function App() {
  const [resume, setResume] = useState('');
  const [job, setJob] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function analyze() {
    setLoading(true); setError('');
    try {
      const response = await fetch('http://localhost:8000/analyze', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({resume, job_description: job}) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Analysis failed');
      setResult(data);
    } catch (caught) { setError(caught.message); }
    finally { setLoading(false); }
  }

  return <main>
    <nav><div className="brand"><Sparkles size={18}/> career copilot</div><span>evidence-led job search</span></nav>
    <section className="intro"><p className="kicker">ROLE INTELLIGENCE / 01</p><h1>Make your next move<br/><em>with receipts.</em></h1><p className="lede">Match your experience to a role, see the proof behind the fit, and leave with language you can actually use.</p><button className="sample" onClick={() => {setResume(sampleResume); setJob(sampleJob)}}>Load sample role <ArrowUpRight size={16}/></button></section>
    <section className="workspace">
      <div className="input-panel"><label><FileText size={16}/> Resume evidence</label><textarea value={resume} onChange={e => setResume(e.target.value)} placeholder="Paste your resume text, projects, and measurable outcomes..."/><label><BriefcaseBusiness size={16}/> Target role</label><textarea value={job} onChange={e => setJob(e.target.value)} placeholder="Paste the job description..."/><button className="analyze" disabled={loading || resume.length < 20 || job.length < 20} onClick={analyze}>{loading ? <><LoaderCircle className="spin" size={17}/> Reading the evidence</> : <>Analyze fit <ArrowUpRight size={17}/></>}</button>{error && <p className="error">{error}</p>}</div>
      <div className="result-panel">{result ? <><div className="score"><div><p className="kicker">GROUNDING CHECK</p><h2>{result.analysis.fit_score}<small>/100</small></h2></div><p>{result.analysis.summary}</p></div><ResultList title="What matches" items={result.analysis.strengths}/><ResultList title="Gaps to close" items={result.analysis.gaps}/><ResultList title="Tailor your application" items={result.analysis.tailoring}/><div className="message"><p className="kicker">RECRUITER NOTE</p><p>{result.analysis.recruiter_message}</p></div><details><summary>Retrieved resume evidence</summary>{result.evidence.map((item, index) => <p key={index}><b>[{index + 1}]</b> {item.text} <small>{item.score}</small></p>)}</details></> : <div className="empty"><Sparkles size={24}/><h3>Your role brief is waiting.</h3><p>Paste both sides of the match to get a score backed by your own experience.</p></div>}</div>
    </section>
  </main>;
}
function ResultList({title, items = []}) { return <div className="list"><h3>{title}</h3>{items.map((item, index) => <p key={index}><span>0{index + 1}</span>{item}</p>)}</div>; }
createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>);
