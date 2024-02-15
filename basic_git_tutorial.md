# Først - setup
## Klone repository
Åpne terminalen i mappa du vil ha repositoriet i.
Skriv inn:
> git clone https://github.com/MSalthe/web_gruppe4_elsys2.git
Dette vil generere en git-mappe på datamaskinen din og lage en lokal kopi av det som er lastet opp her.

## Lag en ny branch
### Lokal branch
Common practice for git er at man ikke jobber på main-branchen. Da unngår man mest mulig krøll. Når man gjør endringer på ting, lager man en heller "gren" av main og jobber på den. Først oppretter du en ny gren lokalt på datamaskinen din:
> git checkout -b (navn på ny branch)

### Remote branch
Når du så har gjort endringer på den lokale branchen, kan du laste opp branchen på GitHub-en ("til remote"). Dette blir videre beskrevet lenger ned.

## Gjøre endringer
### Commit 
Når du har endret en fil, lagt en til, fjernet den etc. og vil "commit"-e til endringene gjør du følgende:
> git commit -a -m "Din melding her"
Dette oppretter en "commit" (som man kan for eksempel kan spole tilbake til senere), legger til alle endringer som har blitt gjort siden sist commit, og legger ved en melding. Meldingen burde beskrive hva som har blitt gjort siden sist commit!

### Push
Når du vil at innholdet på GitHub skal reflektere de endringene du har gjort lokalt på datamaskinen din, bruker du git push. Dette vil laste opp alle commits du har gjort siden sist til de relevante branchene. 

#### Første gang til ny branch
Første gang du pusher til en ny branch, må du opprette den på Github. Da gjør du følgende:
> git push -u origin branch
Da setter du din lokale branch til å "snakke med" en upstream branch (-u) som heter branch. Du kan kalle branchen hva du vil, men navnet må være unikt fra andre branches.

#### Til vanlig
Hvis du allerede har pushet til en remote branch, holder det i fremtiden å gjøre:
> git push



