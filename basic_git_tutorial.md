# Først - setup
## Klone repository
Åpne terminalen i mappa du vil ha repositoriet i.
Skriv inn:
> git clone https://github.com/MSalthe/web_gruppe4_elsys2.git

Dette vil generere en git-mappe på datamaskinen din og lage en lokal kopi av det som er lastet opp her.

## Branches
### Lokal branch
Common practice for git er at man ikke jobber på main-branchen. Da unngår man mest mulig krøll. Helst burde man jobbe på forskjellige branches, og for å unngå merge conflicts, i forskjellige filer. Når man gjør endringer på ting, lager man en heller "gren" av main og jobber på den. Først oppretter du en ny gren lokalt på datamaskinen din:
> git checkout -b (navn på ny branch)

Branchen kan hete hva som helst, men navnet må være unikt fra de andre branchene.

For å bytte mellom lokale branches skriver du
> git checkout (navn på branch)

### Remote branch
Når du så har gjort endringer på den lokale branchen, kan du laste opp branchen på GitHub-en ("til remote"). Dette blir videre beskrevet lenger ned. For å bytte til en branch som allerede finnes på remote, kan du gjøre:
> git checkout -r origin (navn på branch)

## Gjøre endringer
### Commit 
Hvis du har lagt til eller fjernet filer, må du gjøre:
> git add (filnavn)

Dette legger til filen til staging. Hvis du ikke gjør dette blir den ikke "tracked", så de blir ikke med når du commit-er. Hvis du vil at alle filene som er i mappen blir tracked, kan du bytte ut filnavnet med et punktum. (git add .)

Når du har endret en fil og vil "commit"-e til endringene gjør du følgende:
> git commit -a -m "Din melding her"

Dette oppretter en "commit" (som man kan for eksempel kan spole tilbake til senere), legger til alle endringer som har blitt gjort siden sist commit, og legger ved en melding. Meldingen burde beskrive hva som har blitt gjort siden sist commit!

### Push
Når du vil at innholdet på GitHub skal reflektere de endringene du har gjort lokalt på datamaskinen din, bruker du git push. Dette vil laste opp alle commits du har gjort siden sist til de relevante branchene. 

#### Første gang til ny branch
Første gang du pusher til en ny branch, må du opprette den på Github. Da gjør du følgende:
> git push -u origin (navn på branch)

Da setter du din lokale branch til å "snakke med" en upstream branch (-u) som heter det samme som den lokale branchen. Navnet må være likt det du kalte din lokale branch!

#### Til vanlig
Hvis du allerede har pushet til en remote branch, holder det i fremtiden å gjøre:
> git push

## Hente endringer 
Når andre gjør endringer på remote, må du laste dem ned for at ditt lokale filsystem skal reflektere endringene. Det gjør du ved
> git pull

Dette oppdaterer branchen du for øyeblikket befinner deg i. Noen ganger ender dette i en merge conflict, som er litt mer finurlige å løse, men ikke krise. Jeg kan lage en guide om det senere. For å unngå merge conflicts fullstendig kan man jobbe i forskjellige branches.