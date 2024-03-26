%% This simple template was written by Erik Frisk <erik.frisk@liu.se>
%% for use with the CDIO/LIPS courses at Linköping University.
%% 
%% If you find them usefeul, great! If you have constructive suggestions or
%% comments, send me an email and I will consider your comments.

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{lips}[2015/11/01 v1.0 LaTeX class for typesetting LIPS documents]

% Declare options
\DeclareOption{swedish}{\def\@lipslang{swedish}}
\DeclareOption{english}{\def\@lipslang{english}}

\DeclareOption{oneside}{\PassOptionsToClass{oneside}{scrartcl}}
\DeclareOption{twoside}{\PassOptionsToClass{twoside}{scrartcl}}

\DeclareOption{10pt}{\PassOptionsToClass{10pt}{scrartcl}}
\DeclareOption{11pt}{\PassOptionsToClass{11pt}{scrartcl}}
\DeclareOption{12pt}{\PassOptionsToClass{12pt}{scrartcl}}

\ExecuteOptions{english}
\ExecuteOptions{10pt}
\ExecuteOptions{oneside}

\ProcessOptions

% Load scrartcl class
\LoadClass[headinclude,footinclude,a4paper]{scrartcl}

% Load packages
\RequirePackage[
nochapters, % Turn off chapters since this is an article        
%beramono, % Use the Bera Mono font for monospaced text (\texttt)
%eulermath,% Use the Euler font for mathematics
pdfspacing, % Makes use of pdftex’ letter spacing capabilities via the microtype package
dottedtoc
]{classicthesis} % The layout is based on the Classic Thesis style

\RequirePackage{babel}
\RequirePackage[T1]{fontenc}
\RequirePackage[utf8]{inputenc}
\RequirePackage{arsclassica} % Modifies the Classic Thesis package
\RequirePackage{graphicx} % Required for including images
\RequirePackage{hyperref}
\RequirePackage{url}
\RequirePackage{microtype}
\RequirePackage{listings}
\RequirePackage{matlab-prettifier}
%\RequirePackage{verbatim}
%\RequirePackage{palatino}
\RequirePackage{times}
%\RequirePackage{supertabular}
\RequirePackage{longtable}
%\RequirePackage[textwidth=165mm,textheight=230mm]{geometry}
\RequirePackage[textwidth=165mm,textheight=200mm]{geometry}
\RequirePackage{lipsum} % Used for inserting dummy 'Lorem ipsum' text into the template
\RequirePackage{amsmath,amssymb,amsthm} % For including math equations, theorems, symbols, etc
\RequirePackage{varioref} % More descriptive referencing


\def\name@groupemail{Group E-mail}
\def\name@Homepage{Homepage}
\def\name@Orderer{Orderer}
\def\name@Customer{Customer}
\def\name@Supervisor{Supervisor}
\def\name@Responsible{Course Responsible}
\def\name@Phone{Phone}
\def\name@Email{E-mail}
\def\name@Requirement{Requirement}
\def\name@Version{Version}
\def\name@Description{Description}
\def\name@Priority{Priority}
\def\name@contprev{cont. from previous page}
\def\name@contnext{cont. on next page}
\def\name@Author{Author}
\def\name@Date{Date}
\def\name@Reviewed{Reviewed}
\def\name@Approved{Approved}
\def\name@ProjId{Project Identity}

\ifthenelse{\equal{\@lipslang}{swedish}}{
  \def\name@groupemail{Grupp E-post}
  \def\name@Homepage{Hemsida}
  \def\name@Orderer{Beställare}
  \def\name@Customer{Kund}
  \def\name@Supervisor{Handledare}
  \def\name@Responsible{Kursansvarig}
  \def\name@Phone{Tfn}
  \def\name@Email{E-post}
  \def\name@Requirement{Krav}
  \def\name@Version{Version}
  \def\name@Description{Beskrivning}
  \def\name@Priority{Prioritet}
  \def\name@contprev{forts. från föregående sida}
  \def\name@contnext{forts. på nästa sida}
  \def\name@Author{Författare}
  \def\name@Date{Datum}
  \def\name@Reviewed{Granskad}
  \def\name@Approved{Godkänd}
  \def\name@ProjId{Projektidentitet}
}{}

\def\projecttitle#1{\gdef\@projecttitle{#1}}

\def\version#1{\gdef\@version{#1}}

\def\reviewed#1#2{\gdef\@reviewed{#1}\gdef\@revieweddate{#2}}
\def\approved#1#2{\gdef\@approved{#1}\gdef\@approveddate{#2}}

\def\coursename#1{\gdef\@coursename{#1}}
\def\coursecode#1{\gdef\@coursecode{#1}}

\def\courseresponsible#1{\gdef\@courseresponsible{#1}}
\def\courseresponsiblephone#1{\gdef\@courseresponsiblephone{#1}}
\def\courseresponsibleemail#1{\gdef\@courseresponsibleemail{#1}}

\def\supervisor#1{\gdef\@supervisor{#1}}
\def\supervisorphone#1{\gdef\@supervisorphone{#1}}
\def\supervisoremail#1{\gdef\@supervisoremail{#1}}

\def\groupname#1{\gdef\@groupname{#1}}
\def\groupemail#1{\gdef\@groupemail{\url{#1}}}
\def\groupwww#1{\gdef\@groupwww{\url{#1}}}

\def\orderer#1{\gdef\@orderer{#1}}
\def\ordererphone#1{\gdef\@ordererphone{#1}}
\def\ordereremail#1{\gdef\@ordereremail{\url{#1}}}

\def\customer#1{\gdef\@customer{#1}}
\def\customerphone#1{\gdef\@customerphone{#1}}
\def\customeremail#1{\gdef\@customeremail{\url{#1}}}

\def\smalllogo#1{\gdef\@smalllogo{#1}}
\def\biglogo#1{\gdef\@biglogo{#1}}

\renewcommand{\maketitle}{%
  \pagestyle{scrheadings}
  
  \clearscrheadfoot
  \@ifundefined{@smalllogo}{\ihead{}}{\ihead{\includegraphics[width=.2\textwidth]{\@smalllogo}}}
  \chead{\@projecttitle}
  \ohead{\@date}
  \ifoot{\@coursecode\hspace*{5mm}\@coursename\\\@title}
  \ofoot{{\@groupname\\\@groupemail}}

  \pagenumbering{Roman}
  \vspace*{4cm}
  \begin{center}
    \vspace*{3mm}
    {\Huge \@title}\\
    \vspace*{3mm} {\large \@author}\\
    \vspace*{10mm} {\large \@date}\\
    \vspace*{10mm}
    {\large Version \@version}
  \end{center}
  \vfill
  \@ifundefined{@biglogo}{}{
    \begin{figure}[htbp]
      \centering
      \includegraphics[width=0.4\textwidth]{\@biglogo}
    \end{figure}
    \vfill
  }
  \begin{center}
    Status
  \end{center}
  \begin{tabular}{|p{.305\textwidth}|p{.305\textwidth}|p{.305\textwidth}|}
    \hline
    \name@Reviewed & \@reviewed & \@revieweddate\\
    \hline
    \name@Approved & \@approved & \@approveddate \\
    \hline
  \end{tabular}
  \cleardoublepage
  \pagestyle{scrheadings}
}

\newcommand{\makeprojectid}{%
  \begin{center}
    \large\name@ProjId
  \end{center}

  \begin{tabular}{ll}
    \name@groupemail: & \@groupemail\\[5mm]
    \name@Homepage:     & \@groupwww\\[5mm]
    \name@Orderer:      & \@orderer\\
                  & \name@Phone: \@ordererphone\\
                  & \name@Email: \@ordereremail\\[5mm]
    \name@Customer:     & \@customer\\
                  & \name@Phone: \@customerphone\\
                  & \name@Email: \@customeremail\\[5mm]
    \name@Supervisor:   & \@supervisor\\
                  & \name@Phone: \@supervisorphone\\
                  & \name@Email: \@supervisoremail\\[5mm]
    \name@Responsible: & \@courseresponsible\\
                  & \name@Phone: \@courseresponsiblephone\\
                  & \name@Email: \@courseresponsibleemail
  \end{tabular}
}


% Requirements
\newcounter{reqcnt}
\newcommand{\requirementno}{\refstepcounter{reqcnt}\thereqcnt}
% \newenvironment{requirements}{%
%   \begin{center}%
%     \tablefirsthead{\hline \name@Requirement & \name@Description & \name@Priority \\
%       \hline \hline}%
%     \tablehead{\hline \multicolumn{3}{|l|}{\footnotesize\textsl{\name@contprev}}\\\hline \name@Requirement & \name@Description & \name@Priority\\\hline \hline}%
%     \tabletail{\hline \multicolumn{3}{|r|}{\footnotesize\textsl{\name@contnext}}\\\hline}%
%     \tablelasttail{\hline}%
    
%     \begin{supertabular*}{\textwidth}{@{\extracolsep{\fill}}|c|p{100mm}|c|}}{%
%     \end{supertabular*}
%   \end{center}
% }

%\newenvironment{requirements}{%
%  \begin{center}
%    \begin{longtable}{|c|p{100mm}|c|}
%      \hline
%      \name@Requirement & \name@Description & \name@Priority\\
%      \hline
%      \hline
%      \endfirsthead
%      \hline
%      \multicolumn{3}{|l|}%
%      {\footnotesize\textsl{\name@contprev}} \\
%      \hline
%      \name@Requirement & \name@Description & \name@Priority\\
%      \hline
%      \endhead
%      \hline
%      \multicolumn{3}{|r|}%
%      {\footnotesize\textsl{\name@contnext}} \\
%      \hline
%      \endfoot
%      \hline
%      \endlastfoot
%    }{%
%    \end{longtable}
%  \end{center}
%}

\newenvironment{requirements}{%
	\begin{center}
		\begin{longtable}{|c|p{17mm}|p{100mm}|c|}
			\hline
			\name@Requirement & \name@Version &  \name@Description & \name@Priority\\
			\hline
			\hline
			\endfirsthead
			\hline
			\multicolumn{4}{|l|}%
			{\footnotesize\textsl{\name@contprev}} \\
			\hline
			\name@Requirement & \name@Version & \name@Description & \name@Priority\\
			\hline
			\endhead
			\hline
			\multicolumn{4}{|r|}%
			{\footnotesize\textsl{\name@contnext}} \\
			\hline
			\endfoot
			\hline
			\endlastfoot
		}{%
	\end{longtable}
\end{center}
}


\setcounter{tocdepth}{2}
\setlength{\footheight}{26pt}
\setlength{\headheight}{33pt}

\graphicspath{{Figures/}} % Set the default folder for images

\hypersetup{
%draft, % Uncomment to remove all links (useful for printing in black and white)
colorlinks=true, breaklinks=true, bookmarks=true,bookmarksnumbered,
urlcolor=webbrown, linkcolor=RoyalBlue, citecolor=webgreen, % Link colors
pdftitle={}, % PDF title
pdfauthor={}, % PDF Author
pdfsubject={}, % PDF Subject
pdfkeywords={}, % PDF Keywords
pdfcreator={pdfLaTeX}, % PDF Creator
pdfproducer={LaTeX with hyperref and ClassicThesis} % PDF producer
}
