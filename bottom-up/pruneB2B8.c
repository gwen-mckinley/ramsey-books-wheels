/* PLUGIN file to use with geng.c

   To use this, compile geng.c using 
        cc -O3 -DMAXN=32 '-DPLUGIN="pruneB2B8.c"' geng.c gtools.o nauty1.o 
            nautil1.o naugraph1.o schreier.o naurng.o -o gengB2B8
 */

/******************************Configuration***********************************/

#define PLUGIN_INIT plugin_init();

#define PRUNE can_prune

#define PREPRUNE can_preprune

#define SUMMARY summary


/*****************************Statistics***************************************/

static unsigned long long int counts_ramsey_graphs_generated[MAXN+1] = {0};

/*********************************Methods**************************************/

static void
plugin_init() {
    fprintf(stderr, "Plugin for geng for generating (B2,B8)-graphs\n");
}

/******************************************************************************/

/* Assumes that MAXM is 1 (i.e. one_word_sets) */
int
nextelement1(set *set1, int m, int pos) {
    setword setwd;

    if(pos < 0) setwd = set1[0];
    else setwd = set1[0] & BITMASK(pos);

    if(setwd == 0) return -1;
    else return FIRSTBIT(setwd);
}


/******************************************************************************/


//Returns 1 if there is a book of order k
static int contains_Bk(graph* g, int n, int k){
    setword* adj_n = GRAPHROW1(g, n-1, MAXM);

    int v1 = -1;
    while((v1 = nextelement1(adj_n, 1, v1)) >= 0) {
        setword neigh_v1 = *GRAPHROW1(g, v1, MAXM);
        if(POPCOUNT(neigh_v1 & *adj_n) >= k){
            return 1;
        }
        int v2 = v1;
        while((v2 = nextelement1(&neigh_v1, 1, v2)) >= 0) {
            if(POPCOUNT(neigh_v1 & (*GRAPHROW1(g, v2, MAXM))) >= k) {
                return 1; 
            }
        }
    }
    return 0;
}


/******************************************************************************/

static int
can_preprune(graph *g, int n, int maxn) {

    if(contains_Bk(g, n, 2)) {
        return 1; 
    }
    return 0;

}

/******************************************************************************/


static int
can_prune(graph *g, int n, int maxn) {

    complement(g,1,n);
    if(contains_Bk(g, n, 8)){
        complement(g,1,n);
        return 1;
    }
    complement(g,1,n);

    counts_ramsey_graphs_generated[n]++;

    return 0;

}

/*******************************************************************/

static void
SUMMARY(nauty_counter nout, double cpu) {
    for(int i = 3; i <= maxn; i++){
        fprintf(stderr, "Nv=%d, num ramsey graphs generated: %llu\n", 
                i, counts_ramsey_graphs_generated[i]);
    }
    
}
