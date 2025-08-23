#!/usr/bin/env python

from loaddata import load_inv, load_demand, load_jets

LOGGER = []

def get_dyelots(req, inv, jets) -> list[int | tuple[int, int]]:
    """
    Loop through jets:
        If approximate lbs < needed lbs: skip
        
        Load all ports
        If one req:
            Create dyelot and assign
        else:
            Divide ports
            Create two dyelots, assign to corresponding thing
    """
    return [0]

def get_best_job(combs, req, bucket, dmnd, inv, jets) -> int | None:
    """
    Loop through pairs
        Get all dyelots that cover the pair
    
    Get all dyelots that cover the req

    Loop through all dyelots
        Append all jobs and costs
    
    Sort jobs by cost
    Pick the best one and return it
    """
    return 0

def get_req_pairs(req, pnum, matches) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    for match in matches:
        if req + match <= 8:
            pairs.append((req, match))
    return pairs

def make_schedule(dmnd, inv, jets) -> None:
    """
    greige, color, priority, id
    Loop through priorities
        Loop through reqs
            While demand is remaining and can schedule
                grab all matching items
                make pairs that cover everything and fit on one jet
                get the best job from pairs and requirement

                if there is a best job:
                    schedule it
                else:
                    next req
    """
    for pnum in range(1,5):
        for req in dmnd: # dmnd.fullvals()
            bucket = req[pnum]
            while bucket > 10:
                matches = [] # dmnd.get_matches(req)
                pairs = get_req_pairs(bucket, matches)
                job = get_best_job(pairs, bucket, pnum, dmnd, inv, jets)
                if not job:
                    break
                # job.schedule()
                bucket -= 1

def write_output(dmnd, jets, lgr) -> None:
    pass

def main():
    inv = load_inv()
    dmnd = load_demand()
    jets = load_jets()

    make_schedule(dmnd, inv, jets)
    write_output(dmnd, jets, LOGGER)

if __name__ == '__main__':
    main()