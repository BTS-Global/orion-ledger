import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Documents from "./pages/Documents";
import Transactions from "./pages/Transactions";
import Reports from "./pages/Reports";
import IRSForms from "./pages/IRSForms";
import Companies from "./pages/Companies";
import Accounts from "./pages/Accounts";

function Router() {
  return (
    <Layout>
      <Switch>
        <Route path={"/"} component={Dashboard} />
        <Route path={"/dashboard"} component={Dashboard} />
        <Route path="/accounts" component={Accounts} />
        <Route path="/companies" component={Companies} />
        <Route path="/documents" component={Documents} />
        <Route path="/transactions" component={Transactions} />
        <Route path={"/reports"} component={Reports} />
        <Route path={"/irs-forms"} component={IRSForms} />
        <Route path={"/404"} component={NotFound} />
        <Route component={NotFound} />
      </Switch>
    </Layout>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider defaultTheme="light">
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;

