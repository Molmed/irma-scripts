import argparse
import datetime
import os
import pprint
import sys
import tempfile


from typing import List, Callable, Tuple, Optional



def last_access_in_path(fpath: str) -> datetime.datetime:
    # recursively find the last access time for a file under a path
    if os.path.isfile(fpath):
        return datetime.datetime.fromtimestamp(os.stat(fpath).st_atime)
    a_times = []
    for dirpath, dirnames, filenames in os.walk(fpath):
        a_times.extend(
            list(
                filter(
                    lambda x: x,
                    [last_access_in_path(os.path.join(dirpath, dname)) for dname in dirnames] +
                    [last_access_in_path(os.path.join(dirpath, fname)) for fname in filenames])))

    return max(a_times) if a_times else None


def parse_path_and_date_file(path_and_date_file: str) -> List[Tuple[str, datetime.datetime]]:
    # parse a 2-column text file with a name and date (YYMMDD)
    with open(path_and_date_file, 'r') as fh:
        out = [line.strip().split("\t") for line in fh]
        return [(str(o[0]), datetime.datetime.strptime(o[1], "%y%m%d")) for o in out]


def determine_date_cutoff(end_date: datetime.datetime, grace: int) -> datetime.datetime:
    # return a datetime object representing the date at the grace time cutoff
    return end_date - datetime.timedelta(days=grace)


def do_not_remove(fpath: str) -> bool:
    # return true if a path is flagged with "_do_not_remove*"
    fname = os.path.basename(fpath)
    return "_do_not_remove" in fname.lower()


def do_exclude(
        fpath: str,
        modification_date: datetime.datetime,
        date_cutoff: datetime.datetime,
        meta_path_and_dates: List[Tuple[str, datetime.datetime]]) -> bool:

    # if disk modification date is after date_cutoff, return false
    if modification_date >= date_cutoff:
        return False

    fname = os.path.basename(fpath)
    fdir = os.path.dirname(fpath)
    meta_paths = [os.path.basename(p[0]) for p in meta_path_and_dates]
    # if there is a modification date in the meta data after date cutoff, return false
    try:
        ix = meta_paths.index(fname)
        if meta_path_and_dates[ix][1] >= date_cutoff:
            return False
    except ValueError:
        pass

    # if the path is labeled with "_do_not_remove*", return false
    if do_not_remove(fpath):
        return False

    # if a path is accompanied with a "_do_not_remove*"-file on disk or in the meta data,
    # return false
    disk_paths = os.listdir(fdir) if os.path.exists(fdir) else []
    do_not_remove_flags = list(filter(lambda p: do_not_remove(p), disk_paths + meta_paths))
    # strip the "_do_not_remove*" suffix from the names
    do_not_remove_names = [p[0:p.lower().index("_do_not_remove")] for p in do_not_remove_flags]
    if fname in do_not_remove_names:
        return False

    # the path should not be kept because of date or "_do_not_remove*"-indicator, return True
    return True


def include_exclude(
        search_path: str,
        path_and_dates: List[Tuple[str, datetime.datetime]],
        date_cutoff: datetime.datetime,
        meta_path_and_dates: List[Tuple[str, datetime.datetime]],
        exclude_fn: Callable = do_exclude) -> List[List[str]]:
    # determine what objects to include and exclude based on the exclude_fn
    in_ex = [[], []]
    for obj, access_date in path_and_dates:
        in_ex[
            int(
                exclude_fn(
                    os.path.join(search_path, obj),
                    access_date,
                    date_cutoff,
                    meta_path_and_dates))].append(obj)
    return in_ex


def get_path_and_dates(search_path: str) -> List[Tuple[str, datetime.datetime]]:
    # list the objects in the search_path along with the last access time for files beneath it
    return [(obj, last_access_in_path(os.path.join(search_path, obj)))
            for obj in os.listdir(search_path)]


def _sort_objects(
        object_path: str,
        object_date_file: str,
        date_cutoff: datetime.datetime) -> List[List[str]]:
    # sort objects to include and exclude under object_path based on object_date_file and disk
    path_objects_and_dates = get_path_and_dates(object_path)
    meta_objects_and_dates = parse_path_and_date_file(object_date_file)
    in_ex = include_exclude(
        object_path, path_objects_and_dates, date_cutoff, meta_objects_and_dates)
    # if a object is both in include and exclude, let include have precedence
    return [in_ex[0], list(set(in_ex[1]).difference(set(in_ex[0])))]


def sort_projects(
        project_path: str,
        project_date_file: str,
        date_cutoff: datetime.datetime) -> List[List[str]]:
    return _sort_objects(
        object_path=project_path, object_date_file=project_date_file, date_cutoff=date_cutoff)


def sort_runfolders(
        runfolder_path: str,
        runfolder_date_file: str,
        date_cutoff: datetime.datetime) -> List[List[str]]:
    return _sort_objects(
        object_path=runfolder_path, object_date_file=runfolder_date_file, date_cutoff=date_cutoff)


def list_projects_in_runfolder(
        runfolder_path: str, runfolder_project_dir: str = "Unaligned") -> List[str]:
    # list all folders in the runfolder_project dir
    project_dir_path = os.path.join(runfolder_path, runfolder_project_dir)
    return list(filter(
      lambda p: os.path.isdir(os.path.join(project_dir_path, p)),
      os.listdir(project_dir_path)))


def include_runfolders_with_projects(
        runfolder_path: str,
        runfolders_in: List[str],
        runfolders_ex: List[str],
        projects_in: List[str]) -> List[List[str]]:
    # check excluded runfolders and if any contains a project that should be included, move it to
    # the included runfolders list
    in_ex = [runfolders_in, []]
    projects_in_strip_do_not_remove = [
        p[0:p.lower().index("_do_not_remove")]
        for p in filter(lambda p: do_not_remove(p), projects_in)]
    for runfolder_name in runfolders_ex:
        in_ex[int(
          set(projects_in + projects_in_strip_do_not_remove).isdisjoint(
            set(list(map(
                lambda p: p,
                list_projects_in_runfolder(
                    os.path.join(runfolder_path, runfolder_name)))))))].append(runfolder_name)
    return in_ex


def get_include_and_exclude(
        runfolder_path: str, project_path: str, runfolder_date_file: str, project_date_file: str,
        date_cutoff: datetime.datetime) -> List[List[List[str]]]:
    in_ex = [sort_projects(project_path, project_date_file, date_cutoff)]
    runfolders_in_ex = sort_runfolders(runfolder_path, runfolder_date_file, date_cutoff)
    in_ex.append(
      include_runfolders_with_projects(
        runfolder_path, runfolders_in_ex[0], runfolders_in_ex[1], in_ex[0][0]))
    return in_ex


def sort_projects_and_runfolders(
        project_date_file: str,
        runfolder_date_file: str,
        irma_end_date: datetime.datetime,
        grace_period: int,
        runfolder_path: str = "/proj/ngi2016001/incoming",
        project_path: str = "/proj/ngi2016001/nobackup/NGI/ANALYSIS") -> List[Tuple[str, str]]:
    date_cutoff = determine_date_cutoff(irma_end_date, grace_period)
    in_ex = get_include_and_exclude(
      runfolder_path, project_path, runfolder_date_file, project_date_file, date_cutoff)
    in_ex_files = []
    for i, search_path in enumerate([project_path, runfolder_path]):
        prefix = search_path.replace("/", "_")
        tf = []
        for j, typ in enumerate(["include", "exclude"]):
            outfile = f"{prefix}.{typ}.txt"
            with open(outfile, "w") as fh:
                fh.writelines(map(lambda obj: f"{obj}\n", in_ex[i][j]))
            tf.append(outfile)
        in_ex_files.append((tf[0], tf[1]))
    return in_ex_files


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Compile include and exclude lists of files for migration from Irma to Miarka, '
                    'based on grace period and indicator files')
    parser.add_argument(
        'projects',
        help='Two-column, tab-separated file with delivered projects and delivery dates, e.g. '
             'extracted from arteria')
    parser.add_argument(
        'runfolders',
        help='Two-column, tab-separated file with delivered runfolders and delivery dates, e.g. '
             'extracted from arteria')
    parser.add_argument(
        '--irma-end-date',
        required=False,
        default="220331",
        help='The date from which Irma will be unavailable. The date cutoff will be calculated '
             'from this date and the grace period. Expected format is YYMMDD '
             '(default: %(default)s).')
    parser.add_argument(
        '--grace-period',
        required=False,
        default=90,
        help='The grace period in days to keep data after delivery (default: %(default)s days).')

    args = parser.parse_args()
    project = args.project
    genome = args.genome
    pipeline = args.pipeline
    base_path = args.base_path

    project_date_file = args.projects
    runfolder_date_file = args.runfolders
    irma_end_date = datetime.datetime.strptime(args.irma_end_date, "%y%m%d")
    grace_period = int(args.grace_period)
    file_lists = sort_projects_and_runfolders(
      project_date_file, runfolder_date_file, irma_end_date, grace_period)
    pprint.pprint(file_lists)


class TestScript:
    import pytest

    @pytest.fixture
    def end_date(self) -> datetime.datetime:
        return datetime.datetime(year=2022, month=1, day=30)

    @pytest.fixture
    def grace_period(self) -> int:
        return 15

    @pytest.fixture
    def date_cutoff(self, end_date, grace_period) -> datetime.datetime:
        return determine_date_cutoff(end_date=end_date, grace=grace_period)

    @pytest.fixture
    def before_date_cutoff(self, date_cutoff) -> datetime.datetime:
        return date_cutoff - datetime.timedelta(days=10)

    @pytest.fixture
    def after_date_cutoff(self, date_cutoff) -> datetime.datetime:
        return date_cutoff + datetime.timedelta(days=10)

    @pytest.fixture
    def workdir(self, dirname: str = "/tmp") -> tempfile.TemporaryDirectory:
        return tempfile.TemporaryDirectory(dir=dirname)

    @pytest.fixture
    def project_path(self, workdir: tempfile.TemporaryDirectory) -> str:
        return os.path.join(workdir.name, "projects")

    @pytest.fixture
    def project_date_file(self, workdir: tempfile.TemporaryDirectory) -> str:
        return os.path.join(workdir.name, "project_date_file.txt")

    @staticmethod
    def _obj_include_exclude_files(obj_path: str) -> Tuple[str, str]:
        fname = obj_path.replace("/", "_")
        in_ex_files = [f"{fname}.{typ}.txt" for typ in ["include", "exclude"]]
        return in_ex_files[0], in_ex_files[1]

    @pytest.fixture
    def project_include_exclude_files(self, project_path: str) -> Tuple[str, str]:
        return self._obj_include_exclude_files(obj_path=project_path)

    @pytest.fixture
    def runfolder_path(self, workdir: tempfile.TemporaryDirectory) -> str:
        return os.path.join(workdir.name, "runfolders")

    @pytest.fixture
    def runfolder_date_file(self, workdir: tempfile.TemporaryDirectory) -> str:
        return os.path.join(workdir.name, "runfolder_date_file.txt")

    @pytest.fixture
    def runfolder_include_exclude_files(self, runfolder_path: str) -> Tuple[str, str]:
        return self._obj_include_exclude_files(obj_path=runfolder_path)

    @pytest.fixture
    def disk_projects_and_dates(
            self,
            before_date_cutoff: datetime.datetime,
            after_date_cutoff: datetime.datetime) -> List[Tuple[str, datetime.datetime]]:
        return [
            ("AB-1234", before_date_cutoff),
            ("CD-5678_do_not_remove", before_date_cutoff),
            ("c_project", after_date_cutoff),
            ("b_project", before_date_cutoff),
        ]

    @pytest.fixture
    def file_projects_and_dates(
            self,
            before_date_cutoff: datetime.datetime,
            after_date_cutoff: datetime.datetime) -> List[Tuple[str, datetime.datetime]]:
        return [
            ("AB-1234", before_date_cutoff),
            ("CD-5678", before_date_cutoff),
            ("a_project", after_date_cutoff),
            ("b_project_do_not_remove", before_date_cutoff),
        ]

    @pytest.fixture
    def expected_included_projects(self) -> List[str]:
        return sorted([
            "CD-5678_do_not_remove",
            "b_project",
            "c_project"
        ])

    @pytest.fixture
    def expected_excluded_projects(
            self,
            disk_projects_and_dates: List[Tuple[str, datetime.datetime]],
            expected_included_projects: List[str]) -> List[str]:
        return sorted(list(
            set(
                [rf for rf, dt in disk_projects_and_dates]).difference(
                set(expected_included_projects))))

    @pytest.fixture
    def disk_runfolders_and_dates(
            self,
            before_date_cutoff: datetime.datetime,
            after_date_cutoff: datetime.datetime) -> List[Tuple[str, datetime.datetime, List[str]]]:
        return [
            (
                "RunfolderA",
                after_date_cutoff,
                ["ProjA1", "ProjA2"]),
            (
                "RunfolderB",
                before_date_cutoff,
                ["ProjB1", "ProjB2", "CD-5678"]),
            (
                "RunfolderC",
                before_date_cutoff,
                ["ProjC1", "ProjC2"]),
            (
                "RunfolderC_do_not_remove",
                before_date_cutoff,
                []),
            (
                "RunfolderD_do_not_remove_hepp",
                before_date_cutoff,
                ["ProjD1", "ProjD2"]),
            (
                "RunfolderE",
                before_date_cutoff,
                []),
            (
                "RunfolderH",
                before_date_cutoff,
                ["ProjH1", "ProjH2"]),
        ]

    @pytest.fixture
    def file_runfolders_and_dates(
            self,
            before_date_cutoff: datetime.datetime,
            after_date_cutoff: datetime.datetime) -> List[Tuple[str, datetime.datetime]]:
        return [
            ("RunfolderA", before_date_cutoff),
            ("RunfolderD", before_date_cutoff),
            ("RunfolderE_do_not_remove_me", before_date_cutoff),
            ("RunfolderF", after_date_cutoff),
            ("RunfolderG", before_date_cutoff)]

    @pytest.fixture
    def expected_included_runfolders(self) -> List[str]:
        return sorted([
            "RunfolderA",
            "RunfolderB",
            "RunfolderC",
            "RunfolderC_do_not_remove",
            "RunfolderD_do_not_remove_hepp",
            "RunfolderE"
        ])

    @pytest.fixture
    def expected_excluded_runfolders(
            self,
            disk_runfolders_and_dates: List[Tuple[str, datetime.datetime, List[str]]],
            expected_included_runfolders: List[str]) -> List[str]:
        return sorted(list(
            set(
                [rf for rf, dt, _ in disk_runfolders_and_dates]).difference(
                set(expected_included_runfolders))))

    @staticmethod
    def touch_file_with_atime(dirname: str, atime: datetime.datetime) -> str:
        os.makedirs(dirname, exist_ok=True)
        tfile = tempfile.NamedTemporaryFile(dir=dirname, delete=False)
        tfile.close()
        os.utime(tfile.name, times=(atime.timestamp(), atime.timestamp()))
        return tfile.name

    @staticmethod
    def write_obj_dates_to_file(
            obj_list: List[Tuple[str, datetime.datetime]], outfile: str) -> None:
        lines = ["\t".join([obj, objdate.strftime("%y%m%d")]) for obj, objdate in obj_list]
        with open(outfile, "w") as fh:
            fh.writelines([f"{line}\n" for line in lines])

    @pytest.fixture
    def create_projects(
            self,
            file_projects_and_dates: List,
            disk_projects_and_dates: List,
            project_path: str,
            project_date_file: str) -> None:
        for project, projdate in disk_projects_and_dates:
            projdir = os.path.join(project_path, project)
            os.makedirs(projdir)
            self.touch_file_with_atime(projdir, projdate)

        self.write_obj_dates_to_file(file_projects_and_dates, project_date_file)

    @pytest.fixture
    def create_runfolders(
            self,
            file_runfolders_and_dates: List,
            disk_runfolders_and_dates: List,
            runfolder_path: str,
            runfolder_date_file: str) -> None:
        for runfolder, rfdate, projects in disk_runfolders_and_dates:
            rfdir = os.path.join(runfolder_path, runfolder)
            for projname in projects:
                os.makedirs(os.path.join(rfdir, "Unaligned", projname))
            self.touch_file_with_atime(rfdir, rfdate)

        self.write_obj_dates_to_file(file_runfolders_and_dates, runfolder_date_file)

    def test_determine_date_cutoff(self) -> None:
        end_date = datetime.datetime(year=2022, month=1, day=15)
        grace_period = 5
        exp_date = datetime.datetime(year=2022, month=1, day=10)
        assert determine_date_cutoff(end_date, grace_period) == exp_date

    def test_last_access_in_path(
            self,
            workdir: tempfile.TemporaryDirectory,
            end_date: datetime.datetime) -> None:
        dirname = workdir.name
        maxtime = end_date
        offset = 0
        for _ in range(4):
            for _ in range(2):
                maxtime += datetime.timedelta(days=offset)
                self.touch_file_with_atime(dirname, maxtime)
                offset += 1
            dirname = os.path.join(dirname, str(offset))
            os.mkdir(dirname)
        assert last_access_in_path(workdir.name) == maxtime

    def test_do_exclude(
            self,
            workdir: tempfile.TemporaryDirectory,
            date_cutoff: datetime.datetime,
            before_date_cutoff: datetime.datetime,
            after_date_cutoff: datetime.datetime) -> None:

        # assert that a file that is newer than cutoff will NOT be excluded
        assert not do_exclude("this-is-a-path", after_date_cutoff, date_cutoff, [])

        # assert that a path that is older than cutoff will be excluded
        fpath = os.path.join(workdir.name, "this-is-a-path")
        assert do_exclude(fpath, before_date_cutoff, date_cutoff, [])

        # assert that a file that has a meta date that is newer than cutoff will NOT be excluded
        assert not do_exclude(
            "this-is-a-path",
            before_date_cutoff,
            date_cutoff,
            [("this-is-a-path", after_date_cutoff)])

        # assert that a path that is older than cutoff will be excluded
        fpath = os.path.join(workdir.name, "this-is-a-path")
        assert do_exclude(fpath, before_date_cutoff, date_cutoff, [])

        # assert that a file that is older and has meta date that is older than cutoff will be
        # excluded
        assert do_exclude(
            "this-is-a-path",
            before_date_cutoff,
            date_cutoff,
            [("this-is-a-path", before_date_cutoff)])

        # assert that a path with "_do_not_remove"-suffix is NOT excluded
        fpath = os.path.join(workdir.name, "this-is-a-path_dO_nOt_rEmOvE")
        assert not do_exclude(fpath, before_date_cutoff, date_cutoff, [])

        # assert that a path accompanied by a file with "_do_not_remove"-suffix is NOT excluded
        open(fpath, "w").close()
        assert not do_exclude(
            os.path.join(workdir.name, "this-is-a-path"), before_date_cutoff, date_cutoff, [])
        os.unlink(fpath)

        # assert that a path accompanied by a dir with "_do_not_remove"-suffix is NOT excluded
        os.mkdir(fpath)
        assert not do_exclude(
            os.path.join(workdir.name, "this-is-a-path"), before_date_cutoff, date_cutoff, [])
        os.rmdir(fpath)

        # assert that a path accompanied by a list object with "_do_not_remove"-suffix is NOT
        # excluded
        assert not do_exclude(
            os.path.join(workdir.name, "this-is-a-path"),
            before_date_cutoff,
            date_cutoff,
            [(os.path.basename(fpath), date_cutoff)])

        # assert that a path with "_do_not_remove" in the name is NOT excluded
        fpath = os.path.join(workdir.name, "this-is-a-path_do_NOT_remove_me")
        assert not do_exclude(fpath, before_date_cutoff, date_cutoff, [])

        # assert that a path accompanied by a file with "_do_not_remove" in the name is NOT excluded
        open(fpath, "w").close()
        assert not do_exclude(
            os.path.join(workdir.name, "this-is-a-path"), before_date_cutoff, date_cutoff, [])
        os.unlink(fpath)

        # assert that a path accompanied by a dir with "_do_not_remove" in the name is NOT excluded
        os.mkdir(fpath)
        assert not do_exclude(
            os.path.join(workdir.name, "this-is-a-path"), before_date_cutoff, date_cutoff, [])
        os.rmdir(fpath)

        # assert that a path accompanied by a list object with "_do_not_remove" in the name is NOT
        # excluded
        assert not do_exclude(
            os.path.join(workdir.name, "this-is-a-path"),
            before_date_cutoff,
            date_cutoff,
            [(os.path.basename(fpath), date_cutoff)])

    def test_sort_projects(
            self,
            create_projects: None,
            project_date_file: str,
            project_path: str,
            file_projects_and_dates: List[Tuple[str, datetime.datetime]],
            disk_projects_and_dates: List[Tuple[str, datetime.datetime]],
            date_cutoff: datetime.datetime,
            expected_included_projects: List[str],
            expected_excluded_projects: List[str]) -> None:
        observed_inc_ex = sort_projects(
            project_path=project_path,
            project_date_file=project_date_file,
            date_cutoff=date_cutoff)
        assert [sorted(observed_inc_ex[0]), sorted(observed_inc_ex[1])] == \
               [expected_included_projects, expected_excluded_projects]

    def test_sort_runfolders(
            self,
            create_runfolders: None,
            runfolder_date_file: str,
            runfolder_path: str,
            file_runfolders_and_dates: List[Tuple[str, datetime.datetime]],
            disk_runfolders_and_dates: List[Tuple[str, datetime.datetime, List[str]]],
            date_cutoff: datetime.datetime,
            expected_included_runfolders: List[str],
            expected_excluded_runfolders: List[str]) -> None:
        # at this point, RunfolderB should not be included though
        expected_inc_ex = [expected_included_runfolders, expected_excluded_runfolders]
        expected_inc_ex[0].remove("RunfolderB")
        expected_inc_ex[1].append("RunfolderB")
        observed_inc_ex = sort_runfolders(
            runfolder_path=runfolder_path,
            runfolder_date_file=runfolder_date_file,
            date_cutoff=date_cutoff)
        assert [sorted(observed_inc_ex[0]), sorted(observed_inc_ex[1])] == \
               [expected_inc_ex[0], sorted(expected_inc_ex[1])]

    def test_include_runfolders_with_projects(self, runfolder_path: str) -> None:
        for rf in ["A", "B", "C"]:
            rf_path = os.path.join(runfolder_path, f"Runfolder{rf}", "Unaligned")
            for prj in ["1", "2", "3"]:
                prj_path = os.path.join(rf_path, f"Project{rf}{prj}")
                os.makedirs(prj_path)
        runfolders_in = [f"Runfolder{rf}" for rf in "A"]
        runfolders_ex = [f"Runfolder{rf}" for rf in ["B", "C"]]
        projects_in = ["ProjectA1", "ProjectB2"]
        expected_in_ex = [
            sorted([f"Runfolder{rf}" for rf in ["B", "A"]]),
            sorted([f"Runfolder{rf}" for rf in ["C"]])]
        observed_in_ex = include_runfolders_with_projects(
            runfolder_path=runfolder_path,
            runfolders_in=runfolders_in,
            runfolders_ex=runfolders_ex,
            projects_in=projects_in)
        assert [sorted(observed_in_ex[0]), sorted(observed_in_ex[1])] == expected_in_ex

    def test_get_include_and_exclude(
            self,
            create_projects: None,
            create_runfolders: None,
            expected_included_projects: List[str],
            expected_excluded_projects: List[str],
            expected_included_runfolders: List[str],
            expected_excluded_runfolders: List[str],
            runfolder_path: str,
            project_path: str,
            runfolder_date_file: str,
            project_date_file: str,
            date_cutoff: datetime.datetime) -> None:
        in_ex = get_include_and_exclude(
            runfolder_path=runfolder_path,
            project_path=project_path,
            project_date_file=project_date_file,
            runfolder_date_file=runfolder_date_file,
            date_cutoff=date_cutoff)

        assert [sorted(in_ex[0][0]), sorted(in_ex[0][1])] == \
               [expected_included_projects, expected_excluded_projects]
        assert [sorted(in_ex[1][0]), sorted(in_ex[1][1])] == \
               [expected_included_runfolders, expected_excluded_runfolders]

    def test_sort_projects_and_runfolders(
            self,
            create_projects: None,
            create_runfolders: None,
            expected_included_projects: List[str],
            expected_excluded_projects: List[str],
            expected_included_runfolders: List[str],
            expected_excluded_runfolders: List[str],
            project_include_exclude_files: Tuple[str, str],
            runfolder_include_exclude_files: Tuple[str, str],
            workdir: tempfile.TemporaryDirectory,
            runfolder_path: str,
            project_path: str,
            runfolder_date_file: str,
            project_date_file: str,
            end_date: datetime.datetime,
            grace_period: int) -> None:
        os.chdir(workdir.name)
        inc_ex_files = sort_projects_and_runfolders(
            project_date_file=project_date_file,
            runfolder_date_file=runfolder_date_file,
            irma_end_date=end_date,
            grace_period=grace_period,
            project_path=project_path,
            runfolder_path=runfolder_path
        )
        assert inc_ex_files[0] == project_include_exclude_files
        assert inc_ex_files[1] == runfolder_include_exclude_files
        for obj_file, exp_objs in zip(
                [of for of in inc_ex_files[0] + inc_ex_files[1]],
                [expected_included_projects,
                 expected_excluded_projects,
                 expected_included_runfolders,
                 expected_excluded_runfolders]):
            with open(obj_file) as fh:
                obs_objs = [line.strip() for line in fh]
                assert sorted(obs_objs) == sorted(exp_objs)

    #Transfer:
#GENOTYPING
#DELIVERY
#_do_not_remove
#leveransdatum i arteria, 90 dagar
#  - projekt
#  - runolders
#tarballa private/log
#workspace folders for active members
